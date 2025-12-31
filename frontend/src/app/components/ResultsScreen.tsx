import { useState } from "react";
import { Check, Info, Sparkles } from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Checkbox } from "./ui/checkbox";
import { Slider } from "./ui/slider";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
import { SaveModal } from "./SaveModal";
import { motion } from "motion/react";
import { Outfit, OutfitItem, API_BASE_URL } from "../../config/api";

interface ResultsScreenProps {
  outfits: Outfit[];
  alpha: number;
  beta: number;
  pref: number;
  setAlpha: (value: number) => void;
  setBeta: (value: number) => void;
  autoLearn: boolean;
  setAutoLearn: (value: boolean) => void;
  diversity: boolean;
  setDiversity: (value: boolean) => void;
  onGenerateAgain: () => void;
  onFeedback: (selectedIndices: number[]) => void;
  likedOutfits: string[];
  setLikedOutfits: (outfits: string[]) => void;
  dislikedOutfits: string[];
  setDislikedOutfits: (outfits: string[]) => void;
}

export function ResultsScreen({
  outfits,
  alpha,
  beta,
  pref,
  setAlpha,
  setBeta,
  autoLearn,
  setAutoLearn,
  diversity,
  setDiversity,
  onGenerateAgain,
  onFeedback,
  likedOutfits,
  setLikedOutfits,
  dislikedOutfits,
  setDislikedOutfits,
}: ResultsScreenProps) {
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [hoveredOutfit, setHoveredOutfit] = useState<string | null>(null);

  const toggleLike = (id: string, index: number) => {
    let newLikes: string[];
    if (likedOutfits.includes(id)) {
      newLikes = likedOutfits.filter((o) => o !== id);
    } else {
      newLikes = [...likedOutfits, id];
      setDislikedOutfits(dislikedOutfits.filter((o) => o !== id));
    }
    setLikedOutfits(newLikes);

    // Trigger feedback with all currently liked indices
    const selectedIndices = outfits
      .map((o, idx) => (newLikes.includes(o.id) ? idx : -1))
      .filter((idx) => idx !== -1);

    onFeedback(selectedIndices);
  };

  const toggleDislike = (id: string) => {
    if (dislikedOutfits.includes(id)) {
      setDislikedOutfits(dislikedOutfits.filter((o) => o !== id));
    } else {
      setDislikedOutfits([...dislikedOutfits, id]);
      setLikedOutfits(likedOutfits.filter((o) => o !== id));
    }
    // We can also trigger feedback on dislike if the backend supports negative reward
    // For now, feedback is mainly driven by "selections" (likes)
  };

  const getItemImage = (outfit: Outfit, role: string) => {
    const item = outfit.items.find((i: OutfitItem) => i.role === role);
    return item ? `${API_BASE_URL}${item.image_url}` : null;
  };

  return (
    <TooltipProvider>
      <motion.div
        className="max-w-7xl mx-auto px-8 py-12"
        initial={{ opacity: 0, filter: "blur(10px)" }}
        animate={{ opacity: 1, filter: "blur(0px)" }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      >
        <h1 className="mb-12 text-neutral-800 flex items-center gap-3">
          <Sparkles className="w-8 h-8 text-blue-500" />
          Generated Outfits
        </h1>

        {/* Outfit Grid */}
        <div className="grid grid-cols-4 gap-6 mb-12">
          {outfits.map((outfit, index) => {
            const dress = getItemImage(outfit, "dress");
            const top = getItemImage(outfit, "top");
            const bottom = getItemImage(outfit, "bottom");
            const shoes = getItemImage(outfit, "shoes");

            return (
              <motion.div
                key={outfit.id || index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.3,
                  delay: index * 0.05,
                  ease: [0.16, 1, 0.3, 1],
                }}
              >
                <Card
                  className="overflow-hidden relative group"
                  onMouseEnter={() => setHoveredOutfit(outfit.id)}
                  onMouseLeave={() => setHoveredOutfit(null)}
                >
                  <div className="p-3 flex flex-col gap-3 h-full">
                    {dress ? (
                      <>
                        <div className="aspect-[3/5] overflow-hidden rounded-lg bg-neutral-100">
                          <img
                            src={dress}
                            alt="Dress"
                            className="w-full h-full object-cover"
                          />
                        </div>
                        {shoes && (
                          <div className="aspect-[4/3] overflow-hidden rounded-lg bg-neutral-100">
                            <img
                              src={shoes}
                              alt="Shoes"
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                      </>
                    ) : (
                      <>
                        {top && (
                          <div className="aspect-square overflow-hidden rounded-lg bg-neutral-100">
                            <img
                              src={top}
                              alt="Top"
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                        {bottom && (
                          <div className="aspect-[4/3] overflow-hidden rounded-lg bg-neutral-100">
                            <img
                              src={bottom}
                              alt="Bottom"
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                        {shoes && (
                          <div className="aspect-[4/3] overflow-hidden rounded-lg bg-neutral-100">
                            <img
                              src={shoes}
                              alt="Shoes"
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                      </>
                    )}
                  </div>

                  {/* Info Icon */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button className="absolute bottom-3 left-3 w-9 h-9 rounded-full bg-white/95 text-neutral-600 flex items-center justify-center hover:bg-blue-50 transition-all shadow-lg">
                        <Info className="w-4 h-4" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      <div className="space-y-1 text-xs">
                        {outfit.explanation ? (
                          <>
                            <p>• {outfit.explanation.style}</p>
                            <p>• {outfit.explanation.influence}</p>
                            <p>• {outfit.explanation.confidence}</p>
                          </>
                        ) : (
                          <>
                            <p>Score: {outfit.score?.toFixed(2)}</p>
                            <p>Style Fit: {outfit.style_fit?.toFixed(2)}</p>
                            <p>Coherence: {outfit.coherence?.toFixed(2)}</p>
                          </>
                        )}
                      </div>
                    </TooltipContent>
                  </Tooltip>

                  {/* Feedback Control - Like Only */}
                  <div className="absolute bottom-3 right-3">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          className={`w-9 h-9 rounded-full flex items-center justify-center transition-all shadow-lg ${likedOutfits.includes(outfit.id)
                            ? "bg-green-500 text-white"
                            : "bg-white/95 text-neutral-600 hover:bg-green-50"
                            }`}
                          onClick={() => toggleLike(outfit.id, index)}
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>Like</TooltipContent>
                    </Tooltip>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* Session Notice */}
        <div className="mb-8 p-4 bg-blue-50/50 rounded-lg">
          <p className="text-sm text-neutral-600 text-center">
            Learning is session-based and resets on page reload.
          </p>
        </div>

        {/* Controls */}
        <Card className="p-8 mb-8">
          {/* Learning Mode */}
          <div className="mb-8 flex items-center gap-3">
            <Checkbox
              id="auto-learn"
              checked={autoLearn}
              onCheckedChange={(checked) => setAutoLearn(checked as boolean)}
            />
            <label htmlFor="auto-learn" className="text-sm text-neutral-700 cursor-pointer">
              Auto Learn
            </label>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-neutral-400" />
              </TooltipTrigger>
              <TooltipContent>
                AI adapts parameters from your feedback
              </TooltipContent>
            </Tooltip>
          </div>

          {/* Style Parameters */}
          <div className="grid grid-cols-2 gap-8 mb-8">
            {/* Alpha Slider */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-neutral-700">Alpha — Styling Direction</span>
                  <Tooltip>
                    <TooltipTrigger>
                      <Info className="w-4 h-4 text-neutral-400" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      Controls how strongly the system interpolates between your personal style and inspiration styles.
                    </TooltipContent>
                  </Tooltip>
                </div>
                <span className="text-sm text-neutral-600">{alpha.toFixed(2)}</span>
              </div>
              <Slider
                value={[alpha]}
                onValueChange={([value]) => !autoLearn && setAlpha(value)}
                min={0}
                max={1}
                step={0.01}
                disabled={autoLearn}
                className={autoLearn ? "opacity-50" : ""}
              />
              <div className="flex justify-between mt-2 text-xs text-neutral-500">
                <span>Closer to Me</span>
                <span>Closer to Inspiration</span>
              </div>
            </div>

            {/* Beta Slider */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-neutral-700">Beta — Item Selection Bias</span>
                  <Tooltip>
                    <TooltipTrigger>
                      <Info className="w-4 h-4 text-neutral-400" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      Balances stable wardrobe matching versus exploratory item selection.
                    </TooltipContent>
                  </Tooltip>
                </div>
                <span className="text-sm text-neutral-600">{beta.toFixed(2)}</span>
              </div>
              <Slider
                value={[beta]}
                onValueChange={([value]) => !autoLearn && setBeta(value)}
                min={0}
                max={1}
                step={0.01}
                disabled={autoLearn}
                className={autoLearn ? "opacity-50" : ""}
              />
              <div className="flex justify-between mt-2 text-xs text-neutral-500">
                <span>Wardrobe-consistent</span>
                <span>Trend-driven</span>
              </div>
            </div>
          </div>

          {/* Preference Strength */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm text-neutral-700">Preference Strength (Pref)</span>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="w-4 h-4 text-neutral-400" />
                </TooltipTrigger>
                <TooltipContent>
                  Represents the system's confidence in your learned preferences.
                </TooltipContent>
              </Tooltip>
            </div>
            <div className="text-2xl text-neutral-800">{pref.toFixed(2)}</div>
          </div>

          {/* Diversity Control */}
          <div className="flex items-center gap-3">
            <Checkbox
              id="diversity"
              checked={diversity}
              onCheckedChange={(checked) => setDiversity(checked as boolean)}
            />
            <label htmlFor="diversity" className="text-sm text-neutral-700 cursor-pointer">
              Increase Diversity
            </label>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-neutral-400" />
              </TooltipTrigger>
              <TooltipContent>
                Encourages more variation across generated outfits.
              </TooltipContent>
            </Tooltip>
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          <Button variant="outline" onClick={onGenerateAgain}>
            Generate Again
          </Button>
          <Button
            onClick={() => setShowSaveModal(true)}
            disabled={likedOutfits.length === 0}
          >
            Save Selected Outfits
          </Button>
        </div>

        {/* Save Modal */}
        {showSaveModal && (
          <SaveModal
            open={showSaveModal}
            onClose={() => setShowSaveModal(false)}
            likedOutfits={likedOutfits}
            allOutfits={outfits}
            alpha={alpha}
            beta={beta}
            pref={pref}
          />
        )}
      </motion.div>
    </TooltipProvider>
  );
}