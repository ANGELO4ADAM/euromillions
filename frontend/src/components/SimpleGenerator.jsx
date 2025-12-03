import React, { useState } from "react";

const Pill = ({ children, type = "num" }) => (
  <div
    className={
      "inline-flex h-12 w-12 items-center justify-center rounded-full text-xl font-semibold shadow-lg " +
      (type === "num" ? "bg-pink-500 text-white" : "bg-amber-400 text-purple-900")
    }
  >
    {children}
  </div>
);

const NUM_MIN = 1,
  NUM_MAX = 50,
  STAR_MIN = 1,
  STAR_MAX = 12;

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function generateUniqueNumbers(count, min, max) {
  const set = new Set();
  while (set.size < count) {
    set.add(getRandomInt(min, max));
  }
  return Array.from(set).sort((a, b) => a - b);
}

export default function SimpleGenerator() {
  const [generatedCombo, setGeneratedCombo] = useState(null);

  const handleGenerate = () => {
    const combo = {
      numbers: generateUniqueNumbers(5, NUM_MIN, NUM_MAX),
      stars: generateUniqueNumbers(2, STAR_MIN, STAR_MAX),
    };
    setGeneratedCombo(combo);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-950 via-purple-900 to-fuchsia-900 text-white">
      <div className="mx-auto max-w-4xl px-4 pb-16 pt-10">
        <header className="mb-8 text-center">
          <h1 className="bg-gradient-to-r from-pink-400 via-amber-300 to-teal-300 bg-clip-text text-4xl font-extrabold text-transparent">
            Générateur Simple
          </h1>
          <p className="mt-2 max-w-2xl mx-auto text-sm text-purple-100/80">
            Générez une combinaison de numéros et d'étoiles en un seul clic.
          </p>
        </header>

        <div className="rounded-2xl bg-purple-900/60 p-6 shadow-lg shadow-black/40 text-center">
          <div className="mb-6">
            {generatedCombo ? (
              <div className="flex flex-wrap items-center justify-center gap-4">
                {generatedCombo.numbers.map((n) => (
                  <Pill key={`num-${n}`}>{n}</Pill>
                ))}
                <span className="text-xl font-bold text-purple-300 mx-2">+</span>
                {generatedCombo.stars.map((s) => (
                  <Pill key={`star-${s}`} type="star">
                    {s}
                  </Pill>
                ))}
              </div>
            ) : (
              <p className="text-purple-200/70">
                Cliquez sur le bouton pour générer votre grille.
              </p>
            )}
          </div>

          <button
            type="button"
            onClick={handleGenerate}
            className="rounded-full bg-pink-500 px-8 py-3 text-base font-semibold text-white shadow-lg shadow-pink-500/40 hover:bg-pink-400 transition-transform hover:scale-105"
          >
            Générer une nouvelle grille
          </button>
        </div>
      </div>
    </div>
  );
}
