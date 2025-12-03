import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  Award,
  BarChart3,
  Brain,
  RefreshCw,
  Sparkles,
  Star,
  TrendingUp,
  Zap,
} from "lucide-react";

const Pill = ({ children, type = "num" }) => (
  <div
    className={
      "inline-flex h-12 w-12 items-center justify-center rounded-full text-xl font-semibold shadow-lg " +
      (type === "num"
        ? "bg-pink-500 text-white shadow-pink-500/30"
        : "bg-amber-300 text-purple-900 shadow-amber-400/40")
    }
  >
    {children}
  </div>
);

const NUM_MIN = 1;
const NUM_MAX = 50;
const STAR_MIN = 1;
const STAR_MAX = 12;

const historicalDraws = [
  { nums: [7, 12, 19, 33, 43], strs: [3, 9], date: "2024-01-15" },
  { nums: [3, 18, 28, 39, 48], strs: [2, 8], date: "2024-01-12" },
  { nums: [5, 14, 25, 38, 42], strs: [1, 11], date: "2024-01-09" },
  { nums: [2, 11, 23, 31, 47], strs: [5, 10], date: "2024-01-05" },
  { nums: [8, 15, 27, 35, 44], strs: [4, 7], date: "2024-01-02" },
  { nums: [1, 13, 22, 34, 49], strs: [2, 6], date: "2023-12-29" },
  { nums: [9, 17, 26, 37, 45], strs: [3, 12], date: "2023-12-26" },
  { nums: [4, 16, 24, 36, 46], strs: [1, 9], date: "2023-12-22" },
  { nums: [6, 19, 29, 40, 50], strs: [5, 8], date: "2023-12-19" },
  { nums: [10, 20, 30, 41, 48], strs: [2, 11], date: "2023-12-15" },
];

const strategies = [
  {
    id: "random",
    name: "Aléatoire Pure",
    icon: RefreshCw,
    description: "Sélection totalement aléatoire",
    color: "bg-blue-500",
  },
  {
    id: "hot",
    name: "Numéros Chauds",
    icon: TrendingUp,
    description: "Favorise les numéros fréquents",
    color: "bg-red-500",
  },
  {
    id: "cold",
    name: "Numéros Froids",
    icon: Zap,
    description: "Favorise les numéros rares",
    color: "bg-cyan-500",
  },
  {
    id: "balanced",
    name: "Équilibré",
    icon: BarChart3,
    description: "Mix numéros hauts et bas",
    color: "bg-green-500",
  },
  {
    id: "fibonacci",
    name: "Fibonacci",
    icon: Brain,
    description: "Basé sur la suite de Fibonacci",
    color: "bg-purple-500",
  },
  {
    id: "prime",
    name: "Nombres Premiers",
    icon: Star,
    description: "Favorise les nombres premiers",
    color: "bg-yellow-500",
  },
  {
    id: "ai",
    name: "IA Adaptative",
    icon: Brain,
    description: "Apprend des tirages passés",
    color: "bg-gradient-to-r from-purple-600 to-pink-600",
  },
];

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function isPrime(num) {
  if (num < 2) return false;
  for (let i = 2; i <= Math.sqrt(num); i += 1) {
    if (num % i === 0) return false;
  }
  return true;
}

function getFibonacciNumbers(max) {
  const fib = [1, 2];
  while (fib[fib.length - 1] < max) {
    fib.push(fib[fib.length - 1] + fib[fib.length - 2]);
  }
  return fib.filter((n) => n <= max);
}

function getPrize(nums, stars) {
  if (nums === 5 && stars === 2) return { prize: "JACKPOT!", points: 1000 };
  if (nums === 5 && stars === 1) return { prize: "2ème rang", points: 500 };
  if (nums === 5 && stars === 0) return { prize: "3ème rang", points: 250 };
  if (nums === 4 && stars === 2) return { prize: "4ème rang", points: 100 };
  if (nums === 4 && stars === 1) return { prize: "5ème rang", points: 50 };
  if (nums === 3 && stars === 2) return { prize: "6ème rang", points: 40 };
  if (nums === 4 && stars === 0) return { prize: "7ème rang", points: 30 };
  if (nums === 2 && stars === 2) return { prize: "8ème rang", points: 20 };
  if (nums === 3 && stars === 1) return { prize: "9ème rang", points: 15 };
  if (nums === 3 && stars === 0) return { prize: "10ème rang", points: 10 };
  if (nums === 1 && stars === 2) return { prize: "11ème rang", points: 8 };
  if (nums === 2 && stars === 1) return { prize: "12ème rang", points: 5 };
  if (nums === 2 && stars === 0) return { prize: "13ème rang", points: 3 };
  return { prize: "Aucun gain", points: 0 };
}

function generateWithStrategy(strategy, aiModel) {
  let nums = [];
  let strs = [];

  switch (strategy) {
    case "ai": {
      const numPool = Array.from({ length: 50 }, (_, i) => i + 1);
      const starPool = Array.from({ length: 12 }, (_, i) => i + 1);

      const totalWeight = aiModel.weights.reduce((a, b) => a + b, 0);
      const normalizedWeights = aiModel.weights.map((w) => w / totalWeight);

      const totalStarWeight = aiModel.starWeights.reduce((a, b) => a + b, 0);
      const normalizedStarWeights = aiModel.starWeights.map((w) => w / totalStarWeight);

      while (nums.length < 5) {
        const random = Math.random();
        let cumulative = 0;

        for (let i = 0; i < numPool.length; i += 1) {
          cumulative += normalizedWeights[i];
          if (random <= cumulative && !nums.includes(numPool[i])) {
            nums.push(numPool[i]);
            break;
          }
        }

        if (nums.length < 5) {
          const available = numPool.filter((n) => !nums.includes(n));
          if (available.length > 0) {
            nums.push(available[Math.floor(Math.random() * available.length)]);
          }
        }
      }

      while (strs.length < 2) {
        const random = Math.random();
        let cumulative = 0;

        for (let i = 0; i < starPool.length; i += 1) {
          cumulative += normalizedStarWeights[i];
          if (random <= cumulative && !strs.includes(starPool[i])) {
            strs.push(starPool[i]);
            break;
          }
        }

        if (strs.length < 2) {
          const available = starPool.filter((n) => !strs.includes(n));
          if (available.length > 0) {
            strs.push(available[Math.floor(Math.random() * available.length)]);
          }
        }
      }
      break;
    }

    case "random": {
      while (nums.length < 5) {
        const n = getRandomInt(NUM_MIN, NUM_MAX);
        if (!nums.includes(n)) nums.push(n);
      }
      while (strs.length < 2) {
        const s = getRandomInt(STAR_MIN, STAR_MAX);
        if (!strs.includes(s)) strs.push(s);
      }
      break;
    }

    case "hot": {
      const hotPool = Array.from({ length: 25 }, (_, i) => i + 1);
      const regularPool = Array.from({ length: 25 }, (_, i) => i + 26);
      const combinedPool = [...hotPool, ...hotPool, ...regularPool];

      while (nums.length < 5) {
        const n = combinedPool[Math.floor(Math.random() * combinedPool.length)];
        if (!nums.includes(n)) nums.push(n);
      }
      while (strs.length < 2) {
        const s = getRandomInt(STAR_MIN, STAR_MAX);
        if (!strs.includes(s)) strs.push(s);
      }
      break;
    }

    case "cold": {
      const coldPool = Array.from({ length: 25 }, (_, i) => i + 26);
      const lowPool = Array.from({ length: 25 }, (_, i) => i + 1);
      const coldCombined = [...coldPool, ...coldPool, ...lowPool];

      while (nums.length < 5) {
        const n = coldCombined[Math.floor(Math.random() * coldCombined.length)];
        if (!nums.includes(n)) nums.push(n);
      }
      while (strs.length < 2) {
        const s = getRandomInt(STAR_MIN, STAR_MAX);
        if (!strs.includes(s)) strs.push(s);
      }
      break;
    }

    case "balanced": {
      const lowCount = Math.random() < 0.5 ? 2 : 3;

      while (nums.filter((n) => n <= 25).length < lowCount) {
        const n = getRandomInt(NUM_MIN, NUM_MIN + 24);
        if (!nums.includes(n)) nums.push(n);
      }
      while (nums.length < 5) {
        const n = getRandomInt(NUM_MIN + 25, NUM_MAX);
        if (!nums.includes(n)) nums.push(n);
      }
      while (strs.length < 2) {
        const s = getRandomInt(STAR_MIN, STAR_MAX);
        if (!strs.includes(s)) strs.push(s);
      }
      break;
    }

    case "fibonacci": {
      const fibNums = getFibonacciNumbers(NUM_MAX);
      const nonFibNums = Array.from({ length: NUM_MAX }, (_, i) => i + 1).filter(
        (n) => !fibNums.includes(n)
      );

      while (nums.filter((n) => fibNums.includes(n)).length < 3) {
        const n = fibNums[Math.floor(Math.random() * fibNums.length)];
        if (!nums.includes(n)) nums.push(n);
      }
      while (nums.length < 5) {
        const n = nonFibNums[Math.floor(Math.random() * nonFibNums.length)];
        if (!nums.includes(n)) nums.push(n);
      }
      while (strs.length < 2) {
        const s = getRandomInt(STAR_MIN, STAR_MAX);
        if (!strs.includes(s)) strs.push(s);
      }
      break;
    }

    case "prime": {
      const primes = Array.from({ length: NUM_MAX }, (_, i) => i + 1).filter(isPrime);
      const nonPrimes = Array.from({ length: NUM_MAX }, (_, i) => i + 1).filter(
        (n) => !isPrime(n)
      );

      while (nums.filter((n) => isPrime(n)).length < 3) {
        const n = primes[Math.floor(Math.random() * primes.length)];
        if (!nums.includes(n)) nums.push(n);
      }
      while (nums.length < 5) {
        const n = nonPrimes[Math.floor(Math.random() * nonPrimes.length)];
        if (!nums.includes(n)) nums.push(n);
      }
      while (strs.length < 2) {
        const s = getRandomInt(STAR_MIN, STAR_MAX);
        if (!strs.includes(s)) strs.push(s);
      }
      break;
    }

    default:
      break;
  }

  nums.sort((a, b) => a - b);
  strs.sort((a, b) => a - b);

  return { nums, strs };
}

function calculateMatches(generated, actual) {
  const matchedNums = generated.nums.filter((n) => actual.nums.includes(n)).length;
  const matchedStars = generated.strs.filter((s) => actual.strs.includes(s)).length;
  return { matchedNums, matchedStars };
}

export default function EuroMillionsGenerator() {
  const [numbers, setNumbers] = useState([]);
  const [stars, setStars] = useState([]);
  const [strategy, setStrategy] = useState("random");
  const [history, setHistory] = useState([]);
  const [backtestResults, setBacktestResults] = useState([]);
  const [isBacktesting, setIsBacktesting] = useState(false);
  const [showBacktest, setShowBacktest] = useState(false);
  const [aiModel, setAiModel] = useState({
    weights: Array(50).fill(1),
    starWeights: Array(12).fill(1),
    generation: 0,
    totalScore: 0,
    learningRate: 0.1,
  });
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const trainingTimeout = useRef(null);

  const currentStrategy = useMemo(
    () => strategies.find((s) => s.id === strategy),
    [strategy]
  );

  useEffect(() => () => clearTimeout(trainingTimeout.current), []);

  const generate = () => {
    const result = generateWithStrategy(strategy, aiModel);
    setNumbers(result.nums);
    setStars(result.strs);

    const strategyName = strategies.find((s) => s.id === strategy)?.name;
    setHistory((prev) => [
      {
        nums: result.nums,
        strs: result.strs,
        strategy: strategyName,
        time: new Date().toLocaleTimeString(),
      },
      ...prev.slice(0, 6),
    ]);
  };

  const runBacktest = () => {
    setIsBacktesting(true);
    setShowBacktest(true);

    setTimeout(() => {
      const results = strategies.map((strat) => {
        let totalPoints = 0;
        let wins = 0;
        const detailedResults = [];

        for (let i = 0; i < 60; i += 1) {
          const generated = generateWithStrategy(strat.id, aiModel);

          historicalDraws.forEach((draw) => {
            const { matchedNums, matchedStars } = calculateMatches(generated, draw);
            const { prize, points } = getPrize(matchedNums, matchedStars);

            if (points > 0) {
              wins += 1;
              totalPoints += points;
              detailedResults.push({
                nums: generated.nums,
                strs: generated.strs,
                matchedNums,
                matchedStars,
                prize,
                points,
              });
            }
          });
        }

        return {
          strategy: strat.name,
          color: strat.color,
          totalPoints,
          wins,
          avgPoints: (totalPoints / 60).toFixed(2),
          totalTests: 60,
          winRate: ((wins / (60 * historicalDraws.length)) * 100).toFixed(2),
          topWins: detailedResults.sort((a, b) => b.points - a.points).slice(0, 3),
        };
      });

      results.sort((a, b) => b.totalPoints - a.totalPoints);
      setBacktestResults(results);
      setIsBacktesting(false);
    }, 900);
  };

  const trainAI = () => {
    setIsTraining(true);
    setTrainingProgress(0);

    const epochs = 40;
    let currentModel = { ...aiModel };

    const trainStep = (epoch) => {
      trainingTimeout.current = setTimeout(() => {
        const generated = generateWithStrategy("ai", currentModel);

        let bestScore = 0;
        historicalDraws.forEach((draw) => {
          const { matchedNums, matchedStars } = calculateMatches(generated, draw);
          const { points } = getPrize(matchedNums, matchedStars);

          if (points > bestScore) {
            bestScore = points;
          }
        });

        generated.nums.forEach((num) => {
          currentModel.weights[num - 1] *= bestScore > 0
            ? 1 + currentModel.learningRate
            : 1 - currentModel.learningRate * 0.5;
        });

        generated.strs.forEach((star) => {
          currentModel.starWeights[star - 1] *= bestScore > 0
            ? 1 + currentModel.learningRate
            : 1 - currentModel.learningRate * 0.5;
        });

        const maxWeight = Math.max(...currentModel.weights);
        currentModel.weights = currentModel.weights.map((w) => (w / maxWeight) * 10);

        const maxStarWeight = Math.max(...currentModel.starWeights);
        currentModel.starWeights = currentModel.starWeights.map((w) => (w / maxStarWeight) * 10);

        currentModel.generation = epoch + 1;
        currentModel.totalScore += bestScore;

        setAiModel({ ...currentModel });
        setTrainingProgress(((epoch + 1) / epochs) * 100);

        if (epoch < epochs - 1) {
          trainStep(epoch + 1);
        } else {
          setIsTraining(false);
        }
      }, 45);
    };

    trainStep(0);
  };

  const resetAI = () => {
    setAiModel({
      weights: Array(50).fill(1),
      starWeights: Array(12).fill(1),
      generation: 0,
      totalScore: 0,
      learningRate: 0.1,
    });
    setTrainingProgress(0);
    setIsTraining(false);
    clearTimeout(trainingTimeout.current);
  };

  const favoriteNumbers = useMemo(() =>
    aiModel.weights
      .map((w, i) => ({ num: i + 1, weight: Number(w.toFixed(2)) }))
      .sort((a, b) => b.weight - a.weight)
      .slice(0, 5),
  [aiModel.weights]);

  const favoriteStars = useMemo(() =>
    aiModel.starWeights
      .map((w, i) => ({ num: i + 1, weight: Number(w.toFixed(2)) }))
      .sort((a, b) => b.weight - a.weight)
      .slice(0, 2),
  [aiModel.starWeights]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 via-purple-950 to-fuchsia-900 text-white">
      <div className="max-w-6xl mx-auto px-4 py-10 space-y-8">
        <header className="text-center space-y-2">
          <div className="flex items-center justify-center gap-3">
            <Sparkles className="w-12 h-12 text-amber-300" />
            <h1 className="text-5xl font-extrabold bg-gradient-to-r from-pink-400 via-amber-300 to-teal-300 bg-clip-text text-transparent">
              EuroMillions AI Generator
            </h1>
          </div>
          <p className="text-purple-100/80">Stratégies avancées, entraînement IA et backtests rapides.</p>
        </header>

        <section className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 shadow-xl shadow-black/30">
          <div className="flex items-center justify-between gap-3 mb-5 flex-wrap">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-emerald-300" />
              <h2 className="text-xl font-semibold">Stratégies</h2>
            </div>
            <div className="text-xs text-white/60">Sélectionnez une stratégie pour générer votre grille.</div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {strategies.map((strat) => {
              const Icon = strat.icon;
              const isActive = strategy === strat.id;
              return (
                <button
                  key={strat.id}
                  onClick={() => setStrategy(strat.id)}
                  className={`p-4 rounded-xl text-left transition-all duration-200 border border-white/10 hover:border-white/30 ${
                    isActive ? `${strat.color} text-white shadow-lg scale-105` : "bg-white/5 hover:bg-white/10"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <Icon className="w-7 h-7" />
                    {strat.id === "ai" && (
                      <span className="text-xs bg-white/20 rounded px-2 py-1">Gen {aiModel.generation}</span>
                    )}
                  </div>
                  <div className="font-bold text-sm mb-1">{strat.name}</div>
                  <div className="text-xs opacity-90">{strat.description}</div>
                </button>
              );
            })}
          </div>
        </section>

        {strategy === "ai" && (
          <section className="bg-gradient-to-br from-purple-900/60 to-pink-900/60 border border-purple-400/30 rounded-2xl p-6 shadow-lg shadow-black/30">
            <div className="flex items-center gap-3 mb-4">
              <Brain className="w-7 h-7 text-purple-200" />
              <h3 className="text-xl font-semibold">Intelligence Artificielle Adaptative</h3>
            </div>

            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <div className="bg-white/10 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-purple-200">{aiModel.generation}</div>
                <div className="text-sm text-white/70">Générations</div>
              </div>
              <div className="bg-white/10 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-pink-200">{aiModel.totalScore}</div>
                <div className="text-sm text-white/70">Score cumulé</div>
              </div>
              <div className="bg-white/10 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-amber-200">{(aiModel.learningRate * 100).toFixed(0)}%</div>
                <div className="text-sm text-white/70">Taux d'apprentissage</div>
              </div>
            </div>

            {isTraining && (
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-semibold">Entraînement en cours...</span>
                  <span className="text-purple-200 font-semibold">{trainingProgress.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-full transition-all duration-300 rounded-full"
                    style={{ width: `${trainingProgress}%` }}
                  />
                </div>
              </div>
            )}

            <div className="flex gap-4 flex-wrap mb-4">
              <button
                onClick={trainAI}
                disabled={isTraining}
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-semibold hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Brain className="w-5 h-5" />
                {isTraining ? "Apprentissage..." : "Entraîner l'IA"}
              </button>
              <button
                onClick={resetAI}
                disabled={isTraining}
                className="bg-white/10 text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <RefreshCw className="w-5 h-5" />
                Réinitialiser
              </button>
            </div>

            {(favoriteNumbers.length > 0 || favoriteStars.length > 0) && (
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <div className="flex items-center gap-2 mb-3">
                    <Star className="w-5 h-5 text-amber-300" />
                    <h4 className="font-semibold">Top numéros favorisés</h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {favoriteNumbers.map((entry) => (
                      <div
                        key={entry.num}
                        className="px-3 py-2 rounded-full bg-white/10 text-sm flex items-center gap-2"
                      >
                        <Pill>{entry.num}</Pill>
                        <span className="text-white/70 text-xs">poids {entry.weight}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <div className="flex items-center gap-2 mb-3">
                    <Award className="w-5 h-5 text-amber-200" />
                    <h4 className="font-semibold">Top étoiles favorisées</h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {favoriteStars.map((entry) => (
                      <div
                        key={entry.num}
                        className="px-3 py-2 rounded-full bg-white/10 text-sm flex items-center gap-2"
                      >
                        <Pill type="star">{entry.num}</Pill>
                        <span className="text-white/70 text-xs">poids {entry.weight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        <section className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 shadow-xl shadow-black/30">
            <div className="flex items-center justify-between gap-3 mb-4 flex-wrap">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-pink-300" />
                <h3 className="text-xl font-semibold">Générateur</h3>
              </div>
              <div className="text-xs text-white/60">Numéros 1-50 • Étoiles 1-12</div>
            </div>

            <div className="mb-6">
              {numbers.length === 0 ? (
                <p className="text-white/70 text-center">Cliquez sur le bouton pour générer votre grille.</p>
              ) : (
                <div className="flex flex-wrap items-center justify-center gap-4 text-center">
                  {numbers.map((n) => (
                    <Pill key={`num-${n}`}>{n}</Pill>
                  ))}
                  <span className="text-2xl font-bold text-purple-200 mx-1">+</span>
                  {stars.map((s) => (
                    <Pill key={`star-${s}`} type="star">
                      {s}
                    </Pill>
                  ))}
                </div>
              )}
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={generate}
                className="rounded-full bg-pink-500 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-pink-500/40 hover:bg-pink-400 transition-transform hover:scale-105"
              >
                Générer une nouvelle grille
              </button>
              <button
                type="button"
                onClick={runBacktest}
                className="rounded-full bg-white/10 px-5 py-3 text-sm font-semibold text-white hover:bg-white/20 border border-white/20 transition-colors"
              >
                Lancer un backtest
              </button>
              <button
                type="button"
                onClick={() => setShowBacktest((v) => !v)}
                className="rounded-full bg-white/10 px-5 py-3 text-sm font-semibold text-white hover:bg-white/20 border border-white/20 transition-colors"
              >
                {showBacktest ? "Masquer" : "Afficher"} les résultats
              </button>
            </div>

            {isBacktesting && (
              <div className="mt-4 text-sm text-white/80">Backtest en cours...</div>
            )}

            {showBacktest && backtestResults.length > 0 && (
              <div className="mt-6 space-y-4">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-emerald-300" />
                  <h4 className="text-lg font-semibold">Résultats des stratégies</h4>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  {backtestResults.map((result) => (
                    <div
                      key={result.strategy}
                      className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="font-semibold">{result.strategy}</div>
                        <div className="text-xs text-white/60">Win rate {result.winRate}%</div>
                      </div>
                      <div className="text-sm text-white/70 flex flex-wrap gap-3">
                        <span className="px-3 py-1 rounded-full bg-white/10">Points: {result.totalPoints}</span>
                        <span className="px-3 py-1 rounded-full bg-white/10">Gains: {result.wins}</span>
                        <span className="px-3 py-1 rounded-full bg-white/10">Moyenne: {result.avgPoints}</span>
                      </div>
                      {result.topWins.length > 0 && (
                        <div className="text-xs text-white/60">
                          Top tirages :
                          <div className="mt-2 space-y-1">
                            {result.topWins.map((win, index) => (
                              <div key={`${result.strategy}-win-${index}`} className="flex flex-wrap items-center gap-2">
                                <span className="text-white/80">{win.prize}</span>
                                <span className="px-2 py-1 rounded-full bg-white/10">{win.points} pts</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-5 h-5 text-amber-300" />
                <h4 className="font-semibold">Historique récent</h4>
              </div>
              {history.length === 0 ? (
                <p className="text-white/70 text-sm">Aucun tirage généré pour l'instant.</p>
              ) : (
                <div className="space-y-3">
                  {history.map((item, idx) => (
                    <div key={`${item.time}-${idx}`} className="flex items-start gap-3 bg-white/5 rounded-lg p-3 border border-white/10">
                      <div className="text-xs text-white/60 mt-1 w-16">{item.time}</div>
                      <div className="flex-1">
                        <div className="text-sm font-semibold">{item.strategy}</div>
                        <div className="flex flex-wrap gap-2 mt-1 items-center">
                          {item.nums.map((n) => (
                            <Pill key={`hnum-${idx}-${n}`}>{n}</Pill>
                          ))}
                          <span className="text-sm font-bold text-purple-200 mx-1">+</span>
                          {item.strs.map((s) => (
                            <Pill key={`hstar-${idx}-${s}`} type="star">
                              {s}
                            </Pill>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Award className="w-5 h-5 text-emerald-300" />
                <h4 className="font-semibold">Échantillon historique</h4>
              </div>
              <div className="space-y-2 text-sm text-white/80">
                {historicalDraws.slice(0, 5).map((draw) => (
                  <div key={draw.date} className="flex items-center justify-between bg-white/5 rounded-lg px-3 py-2">
                    <span className="text-xs text-white/60">{draw.date}</span>
                    <div className="flex flex-wrap gap-2 items-center">
                      {draw.nums.map((n) => (
                        <span key={`hd-${draw.date}-${n}`} className="px-2 py-1 rounded-full bg-white/10 text-xs">
                          {n}
                        </span>
                      ))}
                      <span className="text-xs font-bold text-purple-200">+</span>
                      {draw.strs.map((s) => (
                        <span key={`hd-${draw.date}-s-${s}`} className="px-2 py-1 rounded-full bg-amber-200 text-purple-900 text-xs font-semibold">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
