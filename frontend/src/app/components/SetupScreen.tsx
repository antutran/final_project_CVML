import { Camera, UserRound } from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { useEffect, useState } from "react";

import { API_BASE_URL } from "../../config/api";

interface KOL {
  id: string;
  name: string;
  style: string;
  display_name: string;
}

interface SetupScreenProps {
  selectedGender: "male" | "female" | null;
  setSelectedGender: (gender: "male" | "female") => void;
  uploadedPhotos: string[];
  setUploadedPhotos: (photos: string[]) => void;
  rawFiles: (File | null)[];
  setRawFiles: (files: (File | null)[]) => void;
  selectedKOLs: string | null;
  setSelectedKOLs: (kol: string | null) => void;
  onGenerate: () => void;
}

export function SetupScreen({
  selectedGender,
  setSelectedGender,
  uploadedPhotos,
  setUploadedPhotos,
  rawFiles,
  setRawFiles,
  selectedKOLs,
  setSelectedKOLs,
  onGenerate,
}: SetupScreenProps) {
  const [kols, setKols] = useState<KOL[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch KOL list from backend
  useEffect(() => {
    const fetchKOLs = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/kol/list`);
        const data = await response.json();
        setKols(data);
      } catch (error) {
        console.error("Failed to fetch KOLs:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchKOLs();
  }, []);

  const handlePhotoUpload = (index: number, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // 1. Store raw file for backend
      const newFiles = [...rawFiles];
      newFiles[index] = file;
      setRawFiles(newFiles);

      // 2. Read for preview
      const reader = new FileReader();
      reader.onload = (e) => {
        const newPhotos = [...uploadedPhotos];
        newPhotos[index] = e.target?.result as string;
        setUploadedPhotos(newPhotos);
      };
      reader.readAsDataURL(file);
    }
  };

  const selectKOL = (id: string) => {
    // Single selection: if already selected, deselect it; otherwise select it
    if (selectedKOLs === id) {
      setSelectedKOLs(null);
    } else {
      setSelectedKOLs(id);
    }
  };

  const isValid = selectedGender && uploadedPhotos.some((p) => p);

  return (
    <div className="max-w-7xl mx-auto px-8 py-12">
      {/* Gender Selection */}
      <div className="mb-16">
        <h2 className="text-center mb-8 text-neutral-600">Select Gender</h2>
        <div className="flex gap-6 justify-center">
          <Card
            className={`w-64 p-8 cursor-pointer transition-all hover:shadow-lg ${selectedGender === "male"
              ? "ring-2 ring-blue-500 shadow-lg shadow-blue-100"
              : "hover:ring-1 hover:ring-neutral-200"
              }`}
            onClick={() => setSelectedGender("male")}
          >
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-blue-50 flex items-center justify-center">
                <UserRound className="w-8 h-8 text-blue-600" />
              </div>
              <span className="text-neutral-900">Male</span>
            </div>
          </Card>
          <Card
            className={`w-64 p-8 cursor-pointer transition-all hover:shadow-lg ${selectedGender === "female"
              ? "ring-2 ring-purple-500 shadow-lg shadow-purple-100"
              : "hover:ring-1 hover:ring-neutral-200"
              }`}
            onClick={() => setSelectedGender("female")}
          >
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-purple-50 flex items-center justify-center">
                <UserRound className="w-8 h-8 text-purple-600" />
              </div>
              <span className="text-neutral-900">Female</span>
            </div>
          </Card>
        </div>
      </div>

      {/* Photo Upload */}
      <div className="mb-16">
        <h2 className="mb-8 text-neutral-600">Upload Your Photos</h2>
        <div className="flex gap-4 justify-center">
          {[0, 1, 2, 3, 4].map((index) => (
            <div key={index} className="relative">
              <input
                type="file"
                id={`photo-upload-${index}`}
                className="hidden"
                accept="image/*"
                onChange={(e) => handlePhotoUpload(index, e)}
              />
              <label
                htmlFor={`photo-upload-${index}`}
                className={`block w-40 h-40 rounded-lg border-2 border-dashed ${uploadedPhotos[index]
                  ? "border-neutral-300"
                  : "border-neutral-200"
                  } flex items-center justify-center cursor-pointer hover:border-neutral-400 transition-colors overflow-hidden`}
              >
                {uploadedPhotos[index] ? (
                  <img
                    src={uploadedPhotos[index]}
                    alt={`Upload ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex flex-col items-center gap-2 text-neutral-400">
                    <Camera className="w-6 h-6" />
                    <span className="text-sm">Add photo</span>
                  </div>
                )}
              </label>
            </div>
          ))}
        </div>
      </div>

      {/* KOL Selection */}
      <div className="mb-16">
        <h2 className="mb-8 text-neutral-600">Choose Style Inspirations</h2>
        {loading ? (
          <div className="text-center text-neutral-400">Loading styles...</div>
        ) : (
          <div className="grid grid-cols-5 gap-6">
            {kols.map((kol) => (
              <Card
                key={kol.id}
                className={`cursor-pointer transition-all hover:shadow-lg ${selectedKOLs === kol.id
                  ? "ring-2 ring-blue-500 shadow-lg"
                  : "hover:ring-1 hover:ring-neutral-200"
                  }`}
                onClick={() => selectKOL(kol.id)}
              >
                <div className="aspect-[3/4] overflow-hidden rounded-t-lg bg-neutral-100">
                  <img
                    src={`${API_BASE_URL}/api/kol/${kol.id}/image`}
                    alt={kol.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-4">
                  <div className="text-sm text-neutral-900 font-medium">{kol.name}</div>
                  <div className="text-xs text-neutral-500 capitalize">{kol.style}</div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Generate Button */}
      <div className="flex justify-center">
        <Button
          size="lg"
          disabled={!isValid}
          onClick={onGenerate}
          className="px-12"
        >
          Generate Outfits
        </Button>
      </div>
    </div>
  );
}
