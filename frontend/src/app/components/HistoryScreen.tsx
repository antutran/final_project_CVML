import { useEffect, useState } from "react";
import { Folder, Calendar, Trash2 } from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";
import { Outfit, API_BASE_URL } from "../../config/api";

interface SavedOutfit {
  folder: string;
  outfits: Outfit[];  // Changed from string[] to Outfit[]
  parameters: {
    alpha: number;
    beta: number;
    pref: number;
  };
  timestamp: string;
}

interface HistoryScreenProps {
  onGenerateFromHistory: () => void;
}

export function HistoryScreen({ onGenerateFromHistory }: HistoryScreenProps) {
  const [savedOutfits, setSavedOutfits] = useState<SavedOutfit[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);

  const loadSavedOutfits = () => {
    const data = JSON.parse(localStorage.getItem("savedOutfits") || "[]");
    setSavedOutfits(data);

    // Update selected folder if current one was deleted
    if (data.length > 0) {
      const folders = Array.from(new Set(data.map((o: SavedOutfit) => o.folder)));
      if (!selectedFolder || !folders.includes(selectedFolder)) {
        setSelectedFolder(folders[0] || null);
      }
    } else {
      setSelectedFolder(null);
    }
  };

  useEffect(() => {
    loadSavedOutfits();
  }, []);

  const deleteFolder = (folderName: string) => {
    if (!confirm(`Delete folder "${folderName}" and all its saved outfits?`)) {
      return;
    }

    // Remove all saved outfits in this folder
    const updatedOutfits = savedOutfits.filter(o => o.folder !== folderName);
    localStorage.setItem("savedOutfits", JSON.stringify(updatedOutfits));


    // Update state immediately
    setSavedOutfits(updatedOutfits);

    // Update selected folder if the deleted one was selected
    if (selectedFolder === folderName) {
      const remainingFolders = Array.from(new Set(updatedOutfits.map((o: SavedOutfit) => o.folder)));
      setSelectedFolder(remainingFolders.length > 0 ? (remainingFolders[0] as string) : null);
    }
  };

  const folders = Array.from(new Set(savedOutfits.map((o) => o.folder)));
  const filteredOutfits = selectedFolder
    ? savedOutfits.filter((o) => o.folder === selectedFolder)
    : savedOutfits;

  const getItemImage = (outfit: Outfit, role: string) => {
    const item = outfit.items?.find((i) => i.role === role);
    return item ? `${API_BASE_URL}${item.image_url}` : null;
  };

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <div className="w-64 border-r border-neutral-200 bg-neutral-50/50">
        <div className="p-6">
          <h3 className="text-neutral-700 mb-4 flex items-center gap-2">
            <Folder className="w-5 h-5" />
            Folders
          </h3>
          <ScrollArea className="h-[calc(100vh-120px)]">
            <div className="space-y-1">
              {folders.map((folder) => (
                <div
                  key={folder}
                  className={`group flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${selectedFolder === folder
                    ? "bg-white text-neutral-900 shadow-sm"
                    : "text-neutral-600 hover:bg-white/50"
                    }`}
                >
                  <button
                    onClick={() => setSelectedFolder(folder)}
                    className="flex-1 text-left"
                  >
                    {folder}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteFolder(folder);
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-50 rounded"
                    title="Delete folder"
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </button>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto px-8 py-12">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-neutral-800">
              {selectedFolder || "All Saved Outfits"}
            </h1>
            <span className="text-sm text-neutral-500">
              {filteredOutfits.length} saved session{filteredOutfits.length !== 1 ? "s" : ""}
            </span>
          </div>

          {filteredOutfits.length === 0 ? (
            <div className="text-center py-20">
              <Folder className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
              <p className="text-neutral-500">No saved outfits yet</p>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-6">
              {filteredOutfits.map((saved, sessionIndex) => (
                <div key={sessionIndex} className="space-y-4">
                  <Card className="overflow-hidden">
                    <div className="p-4">
                      <div className="flex items-center gap-2 text-sm text-neutral-500 mb-3">
                        <Calendar className="w-4 h-4" />
                        {new Date(saved.timestamp).toLocaleDateString()}
                      </div>
                      <div className="space-y-2 mb-4 text-sm">
                        <div className="flex justify-between">
                          <span className="text-neutral-600">Outfits:</span>
                          <span className="text-neutral-900">{saved.outfits.length}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-neutral-600">Alpha:</span>
                          <span className="text-neutral-900">{saved.parameters.alpha.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-neutral-600">Beta:</span>
                          <span className="text-neutral-900">{saved.parameters.beta.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-neutral-600">Pref:</span>
                          <span className="text-neutral-900">{saved.parameters.pref.toFixed(2)}</span>
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={onGenerateFromHistory}
                      >
                        Generate Again
                      </Button>
                    </div>
                  </Card>

                  {/* Display saved outfits */}
                  <div className="grid grid-cols-2 gap-3">
                    {saved.outfits.map((outfit, outfitIndex) => {
                      const dress = getItemImage(outfit, "dress");
                      const top = getItemImage(outfit, "top");
                      const bottom = getItemImage(outfit, "bottom");
                      const shoes = getItemImage(outfit, "shoes");

                      return (
                        <Card key={outfitIndex} className="overflow-hidden">
                          <div className="p-2 flex flex-col gap-2">
                            {dress ? (
                              <>
                                <div className="aspect-[3/5] overflow-hidden rounded-md bg-neutral-100">
                                  <img
                                    src={dress}
                                    alt="Dress"
                                    className="w-full h-full object-cover"
                                  />
                                </div>
                                {shoes && (
                                  <div className="aspect-[4/3] overflow-hidden rounded-md bg-neutral-100">
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
                                  <div className="aspect-square overflow-hidden rounded-md bg-neutral-100">
                                    <img
                                      src={top}
                                      alt="Top"
                                      className="w-full h-full object-cover"
                                    />
                                  </div>
                                )}
                                {bottom && (
                                  <div className="aspect-[4/3] overflow-hidden rounded-md bg-neutral-100">
                                    <img
                                      src={bottom}
                                      alt="Bottom"
                                      className="w-full h-full object-cover"
                                    />
                                  </div>
                                )}
                                {shoes && (
                                  <div className="aspect-[4/3] overflow-hidden rounded-md bg-neutral-100">
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
                        </Card>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
