/**
 * Pokémon Slot Machine Randomizer
 * Spins through random Pokémon with slot-machine effect,
 * plays audio, and displays stats on reveal.
 */

(function () {
  "use strict";

  // ===== CONFIG =====
  const SPIN_DURATION_MS = 3500;
  const INITIAL_TICK_INTERVAL = 50; // ms between ticks at start
  const FINAL_TICK_INTERVAL = 400; // ms between ticks at end
  const IMAGE_BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/";
  const CRY_BASE = "https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/";
  const MAX_STAT = 255; // Max possible base stat (used for bar scaling)

  // Pokémon species color -> CSS background color mapping
  const COLOR_MAP = {
    black: "#303030",
    blue: "#264e86",
    brown: "#6b4226",
    gray: "#5a5a6e",
    green: "#2d6a2d",
    pink: "#b55a7a",
    purple: "#5c3d7a",
    red: "#8b1a1a",
    white: "#6a6a7a",
    yellow: "#8a7a20",
  };

  // ===== DOM ELEMENTS =====
  const app = document.getElementById("app");
  const flashOverlay = document.getElementById("flash-overlay");
  const pokemonImage = document.getElementById("pokemon-image");
  const placeholderText = document.getElementById("placeholder-text");
  const pokemonName = document.getElementById("pokemon-name");
  const pokemonForm = document.getElementById("pokemon-form");
  const statsCard = document.getElementById("stats-card");
  const statsTypes = document.getElementById("stats-types");
  const statsDex = document.getElementById("stats-dex");
  const statsGen = document.getElementById("stats-gen");
  const statsHeight = document.getElementById("stats-height");
  const statsWeight = document.getElementById("stats-weight");
  const statsAbilities = document.getElementById("stats-abilities");
  const spinButton = document.getElementById("spin-button");

  // ===== STATE =====
  let isSpinning = false;
  let audioContext = null;

  // ===== AUDIO ENGINE (Web Audio API) =====
  function getAudioContext() {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.state === "suspended") {
      audioContext.resume();
    }
    return audioContext;
  }

  function playTick(pitch) {
    try {
      const ctx = getAudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "square";
      osc.frequency.value = 800 + pitch * 400;
      gain.gain.value = 0.08;
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.06);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.06);
    } catch (e) {
      // Audio not supported, continue silently
    }
  }

  function playRevealChime() {
    try {
      const ctx = getAudioContext();
      const notes = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6

      notes.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "sine";
        osc.frequency.value = freq;
        gain.gain.value = 0;
        gain.gain.linearRampToValueAtTime(0.12, ctx.currentTime + i * 0.1 + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.1 + 0.4);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(ctx.currentTime + i * 0.1);
        osc.stop(ctx.currentTime + i * 0.1 + 0.5);
      });
    } catch (e) {
      // Audio not supported
    }
  }

  function playCry(pokemonId) {
    try {
      const audio = new Audio(CRY_BASE + pokemonId + ".ogg");
      audio.volume = 0.5;
      audio.play().catch(() => {
        // Try mp3 fallback
        // Some cries may not be available, fail silently
      });
    } catch (e) {
      // Cry not available
    }
  }

  // ===== IMAGE HELPERS =====
  function getImageUrl(pokemonId) {
    return IMAGE_BASE + pokemonId + ".png";
  }

  function preloadImage(url) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(url);
      img.onerror = () => resolve(null);
      img.src = url;
    });
  }

  // ===== DISPLAY HELPERS =====
  function getBackgroundColor(pokemon) {
    return COLOR_MAP[pokemon.color] || COLOR_MAP.white;
  }

  function getFlashClass(pokemon) {
    return pokemon.gen <= 5 ? "flash-white" : "flash-red";
  }

  function formatHeight(decimeters) {
    const meters = decimeters / 10;
    const totalInches = Math.round(meters * 39.3701);
    const feet = Math.floor(totalInches / 12);
    const inches = totalInches % 12;
    return `${meters.toFixed(1)}m (${feet}'${inches.toString().padStart(2, "0")}")`;
  }

  function formatWeight(hectograms) {
    const kg = hectograms / 10;
    const lbs = (kg * 2.20462).toFixed(1);
    return `${kg.toFixed(1)} kg (${lbs} lbs)`;
  }

  function getGenRoman(gen) {
    const roman = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"];
    return roman[gen] || gen.toString();
  }

  function getStatBarColor(statIndex) {
    const colors = ["hp", "atk", "def", "spa", "spd", "spe"];
    return colors[statIndex];
  }

  // ===== UPDATE DISPLAY =====
  function showPokemon(pokemon, isReveal) {
    const imgUrl = getImageUrl(pokemon.id);

    pokemonImage.src = imgUrl;
    pokemonImage.alt = pokemon.name;

    if (isReveal) {
      pokemonImage.className = "reveal";
    } else {
      pokemonImage.className = "spinning";
    }

    // Show name during spin too
    pokemonName.textContent = pokemon.name;
    pokemonName.className = "visible";

    if (pokemon.form) {
      pokemonForm.textContent = pokemon.form;
      pokemonForm.className = "visible";
    } else {
      pokemonForm.textContent = "";
      pokemonForm.className = "";
    }
  }

  function showStats(pokemon) {
    // Types
    statsTypes.innerHTML = "";
    pokemon.types.forEach((type) => {
      const badge = document.createElement("span");
      badge.className = `type-badge type-${type.toLowerCase()}`;
      badge.textContent = type;
      statsTypes.appendChild(badge);
    });

    // Info
    statsDex.textContent = `#${pokemon.dex.toString().padStart(4, "0")}`;
    statsGen.textContent = `Gen ${getGenRoman(pokemon.gen)}`;
    statsHeight.textContent = formatHeight(pokemon.height);
    statsWeight.textContent = formatWeight(pokemon.weight);
    statsAbilities.textContent = pokemon.abilities.join(", ");

    // Stat bars
    const statNames = ["hp", "atk", "def", "spa", "spd", "spe"];
    statNames.forEach((name, i) => {
      const value = pokemon.stats[i];
      const bar = document.querySelector(`.stat-bar[data-stat="${name}"]`);
      const valueEl = document.querySelector(`.stat-value[data-stat="${name}"]`);

      if (bar) {
        bar.style.width = "0%";
        // Animate after a tiny delay for the transition to work
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            bar.style.width = Math.min((value / MAX_STAT) * 100, 100) + "%";
          });
        });
      }
      if (valueEl) {
        valueEl.textContent = value;
      }
    });

    // Show the card
    statsCard.className = "visible";
  }

  function hideStats() {
    statsCard.className = "hidden";
    // Reset stat bars
    document.querySelectorAll(".stat-bar").forEach((bar) => {
      bar.style.width = "0%";
    });
  }

  function setBackground(color) {
    app.style.backgroundColor = color;
    // Also update meta theme-color for mobile browser chrome
    const metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) metaTheme.content = color;
  }

  // ===== SPIN LOGIC =====
  function getRandomPokemon() {
    return POKEMON_DATA[Math.floor(Math.random() * POKEMON_DATA.length)];
  }

  async function spin() {
    if (isSpinning) return;
    isSpinning = true;

    // Initialize audio on user gesture
    getAudioContext();

    // Reset UI
    placeholderText.classList.add("hidden");
    hideStats();
    spinButton.classList.add("spinning");

    // Pick the final result upfront
    const finalPokemon = getRandomPokemon();

    // Preload the final image
    preloadImage(getImageUrl(finalPokemon.id));

    // Slot machine cycling
    const startTime = Date.now();
    let lastTickTime = 0;

    function tick() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / SPIN_DURATION_MS, 1);

      // Easing: slow down exponentially towards the end
      const eased = 1 - Math.pow(1 - progress, 3);

      // Current interval between ticks
      const currentInterval =
        INITIAL_TICK_INTERVAL +
        (FINAL_TICK_INTERVAL - INITIAL_TICK_INTERVAL) * eased;

      if (elapsed - lastTickTime >= currentInterval) {
        lastTickTime = elapsed;

        // Show random pokemon during spin (use final one on last tick)
        let current;
        if (progress >= 1) {
          current = finalPokemon;
        } else {
          current = getRandomPokemon();
        }

        showPokemon(current, false);
        playTick(1 - progress);

        // Flash background based on generation
        const flashClass = getFlashClass(current);
        flashOverlay.className = flashClass;
        setTimeout(() => {
          flashOverlay.className = "";
        }, currentInterval * 0.5);
      }

      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        // Reveal!
        reveal(finalPokemon);
      }
    }

    requestAnimationFrame(tick);
  }

  function reveal(pokemon) {
    // Stop spinning animation on button
    spinButton.classList.remove("spinning");

    // Set background to Pokémon's official color
    setBackground(getBackgroundColor(pokemon));

    // Show the final Pokémon with reveal animation
    showPokemon(pokemon, true);

    // Flash overlay clear
    flashOverlay.className = "";

    // Play reveal audio
    playRevealChime();

    // Play Pokémon cry after a short pause
    setTimeout(() => {
      playCry(pokemon.id);
    }, 300);

    // Show stats with delay for dramatic effect
    setTimeout(() => {
      showStats(pokemon);
    }, 500);

    // Re-enable spinning
    setTimeout(() => {
      isSpinning = false;
    }, 1000);
  }

  // ===== EVENT LISTENERS =====
  spinButton.addEventListener("click", spin);

  // Also allow spacebar / enter to spin
  document.addEventListener("keydown", (e) => {
    if (e.key === " " || e.key === "Enter") {
      e.preventDefault();
      spin();
    }
  });

  // ===== INIT =====
  function init() {
    // Set initial dark background
    setBackground("#1a1a2e");

    // Log data info
    console.log(
      `Pokémon Randomizer loaded: ${POKEMON_DATA.length} Pokémon entries`
    );
  }

  init();
})();
