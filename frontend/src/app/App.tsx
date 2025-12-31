import { useState, useEffect } from "react";
import { SetupScreen } from "./components/SetupScreen";
import { ProcessingScreen } from "./components/ProcessingScreen";
import { ResultsScreen } from "./components/ResultsScreen";
import { HistoryScreen } from "./components/HistoryScreen";
import { Button } from "./components/ui/button";
import { History, House } from "lucide-react";
import { AnimatePresence } from "motion/react";
import { apiClient, Outfit } from "../config/api";

type Screen = "setup" | "processing" | "results" | "history";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>("setup");

  // Session state
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Setup state
  const [selectedGender, setSelectedGender] = useState<"male" | "female" | null>(null);
  const [uploadedPhotos, setUploadedPhotos] = useState<string[]>(Array(5).fill(""));
  const [rawFiles, setRawFiles] = useState<(File | null)[]>(Array(5).fill(null));
  const [selectedKOLs, setSelectedKOLs] = useState<string | null>(null);

  // Results state
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [alpha, setAlpha] = useState(0.62);
  const [beta, setBeta] = useState(0.45);
  const [pref, setPref] = useState(0.78);
  const [conf, setConf] = useState(0.0);
  const [step, setStep] = useState(0);
  const [autoLearn, setAutoLearn] = useState(true);
  const [diversity, setDiversity] = useState(false);
  const [likedOutfits, setLikedOutfits] = useState<string[]>([]);
  const [dislikedOutfits, setDislikedOutfits] = useState<string[]>([]);

  // Clear history on page load/reload
  useEffect(() => {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('saved_')) {
        localStorage.removeItem(key);
      }
    });
  }, []);

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        const id = await apiClient.createSession();
        setSessionId(id);
        console.log("Session initialized:", id);
      } catch (error) {
        console.error("Failed to initialize session:", error);
      }
    };
    initSession();
  }, []);

  const handleGenerate = async () => {
    if (!sessionId || !selectedGender || !selectedKOLs) return;

    try {
      setCurrentScreen("processing");

      // 1. Set Gender
      await apiClient.setGender(sessionId, selectedGender);

      // 2. Select KOL
      await apiClient.selectKOL(sessionId, selectedKOLs);

      // 3. Upload Images
      const filesToUpload = rawFiles.filter((f): f is File => f !== null);
      if (filesToUpload.length > 0) {
        await apiClient.uploadImages(sessionId, filesToUpload);
        // 4. Generate Embeddings
        await apiClient.generateEmbeddings(sessionId);
      } else {
        // If no images uploaded, just generate with KOL (this might fail depending on backend requirement)
        console.warn("No user images uploaded, continuing with KOL only...");
      }

      // 5. Generate Outfits with auto_learn enabled initially
      const response = await apiClient.generateOutfits(sessionId, {
        autoLearn: true,
        diversity: diversity,
      });

      setOutfits(response.outfits);
      setAlpha(response.alpha);
      setBeta(response.beta);
      setPref(response.pref);
      setConf(response.conf);
      setStep(response.step);

      setCurrentScreen("results");
    } catch (error) {
      console.error("Generation flow failed:", error);
      alert("Failed to generate outfits. Please check if the backend is running and CLIP is installed.");
      setCurrentScreen("setup");
    }
  };

  const handleGenerateAgain = async () => {
    if (!sessionId) return;

    try {
      // Step 1: Send feedback for currently liked outfits (if any)
      if (likedOutfits.length > 0) {
        const selectedIndices = outfits
          .map((o, idx) => (likedOutfits.includes(o.id) ? idx : -1))
          .filter((idx) => idx !== -1);

        if (selectedIndices.length > 0) {
          const response = await apiClient.submitFeedback(
            sessionId,
            selectedIndices,
            outfits
          );

          // Update learned parameters from feedback
          if (response.updated) {
            setPref(response.pref);
            setConf(response.conf);
            setBeta(response.beta);
          }
        }
      }

      // Step 2: Clear selections and show processing
      setLikedOutfits([]);
      setDislikedOutfits([]);
      setCurrentScreen("processing");

      // Step 3: Generate new outfits with updated/learned parameters
      // Pass manual alpha/beta when autoLearn is false
      const response = await apiClient.generateOutfits(sessionId, {
        autoLearn: autoLearn,
        manualAlpha: autoLearn ? undefined : alpha,
        manualBeta: autoLearn ? undefined : beta,
        diversity: diversity,
      });

      setOutfits(response.outfits);
      setAlpha(response.alpha);
      setBeta(response.beta);
      setPref(response.pref);
      setConf(response.conf);
      setStep(response.step);

      setCurrentScreen("results");
    } catch (error) {
      console.error("Generate again failed:", error);
      setCurrentScreen("results");
    }
  };

  const handleFeedback = async (selectedIndices: number[]) => {
    if (!sessionId) return;

    try {
      const response = await apiClient.submitFeedback(
        sessionId,
        selectedIndices,
        outfits
      );

      if (response.updated) {
        setPref(response.pref);
        setConf(response.conf);
        setBeta(response.beta);
      }
    } catch (error) {
      console.error("Feedback submission failed:", error);
    }
  };

  const handleGenerateFromHistory = () => {
    handleGenerate();
  };

  const handleReset = () => {
    // Clear all saved outfit history from localStorage
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('saved_')) {
        localStorage.removeItem(key);
      }
    });

    // Navigate to setup screen
    setCurrentScreen("setup");
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      {currentScreen !== "history" && currentScreen !== "processing" && (
        <header className="border-b border-neutral-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500" />
              <h1 className="text-neutral-900">AI Fashion Studio</h1>
            </div>
            <nav className="flex items-center gap-2">
              {currentScreen === "results" && (
                <Button
                  variant="ghost"
                  onClick={handleReset}
                >
                  <House className="w-4 h-4 mr-2" />
                  New Session
                </Button>
              )}
              <Button
                variant="ghost"
                onClick={() => setCurrentScreen("history")}
              >
                <History className="w-4 h-4 mr-2" />
                History
              </Button>
            </nav>
          </div>
        </header>
      )}

      {/* Screen Router */}
      <AnimatePresence mode="wait">
        {currentScreen === "setup" && (
          <SetupScreen
            key="setup"
            selectedGender={selectedGender}
            setSelectedGender={setSelectedGender}
            uploadedPhotos={uploadedPhotos}
            setUploadedPhotos={setUploadedPhotos}
            rawFiles={rawFiles}
            setRawFiles={setRawFiles}
            selectedKOLs={selectedKOLs}
            setSelectedKOLs={setSelectedKOLs}
            onGenerate={handleGenerate}
          />
        )}

        {currentScreen === "processing" && (
          <ProcessingScreen key="processing" onComplete={() => { }} />
        )}

        {currentScreen === "results" && (
          <ResultsScreen
            key="results"
            outfits={outfits}
            alpha={alpha}
            beta={beta}
            pref={pref}
            setAlpha={setAlpha}
            setBeta={setBeta}
            autoLearn={autoLearn}
            setAutoLearn={setAutoLearn}
            diversity={diversity}
            setDiversity={setDiversity}
            onGenerateAgain={handleGenerateAgain}
            likedOutfits={likedOutfits}
            setLikedOutfits={setLikedOutfits}
            dislikedOutfits={dislikedOutfits}
            setDislikedOutfits={setDislikedOutfits}
            onFeedback={handleFeedback}
          />
        )}

        {currentScreen === "history" && (
          <div key="history">
            <header className="border-b border-neutral-200 bg-white/80 backdrop-blur-sm">
              <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500" />
                  <h1 className="text-neutral-900">AI Fashion Studio</h1>
                </div>
                <Button
                  variant="ghost"
                  onClick={handleReset}
                >
                  <House className="w-4 h-4 mr-2" />
                  New Session
                </Button>
              </div>
            </header>
            <HistoryScreen onGenerateFromHistory={handleGenerateFromHistory} />
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}