import { useState, useEffect } from "react";
import { FolderPlus, Folder } from "lucide-react";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { RadioGroup, RadioGroupItem } from "./ui/radio-group";
import { Outfit } from "../../config/api";

interface SaveModalProps {
  open: boolean;
  onClose: () => void;
  likedOutfits: string[];
  allOutfits: Outfit[];
  alpha: number;
  beta: number;
  pref: number;
}

export function SaveModal({
  open,
  onClose,
  likedOutfits,
  allOutfits,
  alpha,
  beta,
  pref,
}: SaveModalProps) {
  const [folders, setFolders] = useState<string[]>([]);
  const [selectedFolder, setSelectedFolder] = useState("");
  const [newFolderName, setNewFolderName] = useState("");
  const [showNewFolder, setShowNewFolder] = useState(false);

  // Load existing folders from localStorage when modal opens
  useEffect(() => {
    if (open) {
      const savedData = JSON.parse(localStorage.getItem("savedOutfits") || "[]");
      const existingFolders = Array.from(new Set(savedData.map((s: any) => s.folder)));
      setFolders(existingFolders);

      // If no folders exist, show new folder input
      if (existingFolders.length === 0) {
        setShowNewFolder(true);
      } else {
        setShowNewFolder(false);
        setSelectedFolder(existingFolders[0] || "");
      }
    }
  }, [open]);

  const handleSave = () => {
    const folderToUse = showNewFolder ? newFolderName : selectedFolder;

    if (!folderToUse) return;

    // Add new folder if creating one
    if (showNewFolder && newFolderName && !folders.includes(newFolderName)) {
      setFolders([...folders, newFolderName]);
    }

    // Save to localStorage - save full outfit data for liked outfits
    const likedOutfitObjects = allOutfits.filter(outfit =>
      likedOutfits.includes(outfit.id)
    );

    const savedData = {
      folder: folderToUse,
      outfits: likedOutfitObjects,  // Save full outfit objects
      parameters: { alpha, beta, pref },
      timestamp: new Date().toISOString(),
    };

    const existing = JSON.parse(localStorage.getItem("savedOutfits") || "[]");
    localStorage.setItem("savedOutfits", JSON.stringify([...existing, savedData]));

    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Save Selected Outfits</DialogTitle>
          <DialogDescription>
            Choose a folder to save {likedOutfits.length} outfit{likedOutfits.length !== 1 ? "s" : ""}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {folders.length > 0 && !showNewFolder && (
            <div>
              <Label className="mb-3 block">Select Folder</Label>
              <RadioGroup value={selectedFolder} onValueChange={setSelectedFolder}>
                {folders.map((folder) => (
                  <div key={folder} className="flex items-center space-x-2 mb-2">
                    <RadioGroupItem value={folder} id={folder} />
                    <Label htmlFor={folder} className="flex items-center gap-2 cursor-pointer">
                      <Folder className="w-4 h-4 text-neutral-500" />
                      {folder}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>
          )}

          {showNewFolder && (
            <div>
              <Label htmlFor="folder-name">New Folder Name</Label>
              <Input
                id="folder-name"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                placeholder="Enter folder name"
                className="mt-2"
              />
            </div>
          )}

          <Button
            variant="outline"
            className="w-full"
            onClick={() => setShowNewFolder(!showNewFolder)}
          >
            <FolderPlus className="w-4 h-4 mr-2" />
            {showNewFolder ? "Select Existing Folder" : "Create New Folder"}
          </Button>

          <div className="p-4 bg-neutral-50 rounded-lg text-sm space-y-1">
            <p className="text-neutral-600">Will save:</p>
            <p className="text-neutral-800">• {likedOutfits.length} outfit{likedOutfits.length !== 1 ? "s" : ""}</p>
            <p className="text-neutral-800">• Alpha: {alpha.toFixed(2)}, Beta: {beta.toFixed(2)}, Pref: {pref.toFixed(2)}</p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={!showNewFolder ? !selectedFolder : !newFolderName}
          >
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
