import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import { Card } from "./ui/card";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Cell } from "recharts";
import { motion, AnimatePresence } from "motion/react";

interface ProcessingScreenProps {
  onComplete: () => void;
}

const STEPS = [
  { id: 1, label: "Extracting visual features" },
  { id: 2, label: "Building user style embedding" },
  { id: 3, label: "Conditioning inspiration style" },
  { id: 4, label: "Interpolating target style" },
  { id: 5, label: "Matching wardrobe items" },
];

const generateEmbeddingData = (phase: number) => {
  const userPoint = { x: 20, y: 30, type: "user" };
  const inspirationPoint = { x: 70, y: 60, type: "inspiration" };
  
  if (phase < 4) {
    return [userPoint, inspirationPoint];
  }
  
  // Add target point after interpolation step
  const targetPoint = {
    x: userPoint.x + (inspirationPoint.x - userPoint.x) * 0.6,
    y: userPoint.y + (inspirationPoint.y - userPoint.y) * 0.6,
    type: "target",
  };
  
  return [userPoint, inspirationPoint, targetPoint];
};

// Particle component for flowing animation
const Particle = ({ delay, index }: { delay: number; index: number }) => {
  const angle = (index / 12) * Math.PI * 2;
  const startX = Math.cos(angle) * 150;
  const startY = Math.sin(angle) * 150;
  
  return (
    <motion.div
      className="absolute w-1.5 h-1.5 rounded-full bg-blue-400/40"
      initial={{ 
        x: startX, 
        y: startY, 
        opacity: 0,
        scale: 0 
      }}
      animate={{ 
        x: 0, 
        y: 0, 
        opacity: [0, 0.6, 0],
        scale: [0, 1, 0]
      }}
      transition={{
        duration: 2,
        delay,
        repeat: Infinity,
        ease: [0.16, 1, 0.3, 1]
      }}
      style={{
        left: '50%',
        top: '50%',
      }}
    />
  );
};

export function ProcessingScreen({ onComplete }: ProcessingScreenProps) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= STEPS.length - 1) {
          clearInterval(timer);
          setTimeout(() => onComplete(), 500);
          return prev;
        }
        return prev + 1;
      });
    }, 800);

    return () => clearInterval(timer);
  }, [onComplete]);

  const embeddingData = generateEmbeddingData(currentStep);

  return (
    <motion.div 
      className="h-screen flex items-center justify-center bg-neutral-50/50 relative overflow-hidden"
      initial={{ opacity: 0, filter: "blur(20px)" }}
      animate={{ opacity: 1, filter: "blur(0px)" }}
      exit={{ opacity: 0, filter: "blur(20px)" }}
      transition={{ duration: 0.3 }}
    >
      {/* Animated background glow */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-transparent to-purple-50/50"
        animate={{
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Flowing particles */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        {Array.from({ length: 12 }).map((_, i) => (
          <Particle key={i} index={i} delay={i * 0.15} />
        ))}
      </div>

      <div className="max-w-6xl w-full px-8 relative z-10">
        <motion.div 
          className="grid grid-cols-2 gap-8"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          {/* Left Panel - AI Pipeline */}
          <Card className="p-8 backdrop-blur-sm bg-white/80 border-neutral-200/60">
            <h3 className="mb-8 text-neutral-700">AI Pipeline</h3>
            <div className="space-y-6">
              {STEPS.map((step, index) => {
                const isComplete = index < currentStep;
                const isActive = index === currentStep;

                return (
                  <motion.div 
                    key={step.id} 
                    className="flex items-center gap-4"
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ 
                      duration: 0.3, 
                      delay: index * 0.1,
                      ease: [0.16, 1, 0.3, 1]
                    }}
                  >
                    <motion.div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        isComplete
                          ? "bg-green-100"
                          : isActive
                          ? "bg-blue-100"
                          : "bg-neutral-100"
                      }`}
                      animate={isActive ? {
                        boxShadow: [
                          "0 0 0 0 rgba(59, 130, 246, 0)",
                          "0 0 0 8px rgba(59, 130, 246, 0.1)",
                          "0 0 0 0 rgba(59, 130, 246, 0)",
                        ],
                      } : {}}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                    >
                      {isComplete ? (
                        <motion.div
                          initial={{ scale: 0, rotate: -180 }}
                          animate={{ scale: 1, rotate: 0 }}
                          transition={{ 
                            duration: 0.3,
                            ease: [0.34, 1.56, 0.64, 1]
                          }}
                        >
                          <Check className="w-4 h-4 text-green-600" />
                        </motion.div>
                      ) : isActive ? (
                        <motion.div
                          className="w-2 h-2 rounded-full bg-blue-600"
                          animate={{
                            scale: [1, 1.2, 1],
                            opacity: [1, 0.6, 1]
                          }}
                          transition={{
                            duration: 1,
                            repeat: Infinity,
                            ease: "easeInOut"
                          }}
                        />
                      ) : (
                        <div className="w-2 h-2 rounded-full bg-neutral-300" />
                      )}
                    </motion.div>
                    <motion.div
                      className={`${
                        isComplete
                          ? "text-neutral-600"
                          : isActive
                          ? "text-neutral-900"
                          : "text-neutral-400"
                      }`}
                      animate={isActive ? {
                        opacity: [0.8, 1, 0.8]
                      } : {}}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                    >
                      {step.label}
                    </motion.div>
                  </motion.div>
                );
              })}
            </div>
          </Card>

          {/* Right Panel - Embedding Visualization */}
          <Card className="p-8 backdrop-blur-sm bg-white/80 border-neutral-200/60 relative overflow-hidden">
            {/* Shimmer effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
              initial={{ x: "-100%" }}
              animate={{ x: "200%" }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 1,
                ease: "easeInOut"
              }}
            />
            
            <h3 className="mb-4 text-neutral-700 relative z-10">Shared Visual Embedding Space</h3>
            <div className="h-80 relative z-10">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart
                  margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                  <XAxis type="number" dataKey="x" domain={[0, 100]} hide />
                  <YAxis type="number" dataKey="y" domain={[0, 100]} hide />
                  <Scatter 
                    data={embeddingData} 
                    isAnimationActive={true}
                    animationDuration={400}
                    animationEasing="ease-out"
                  >
                    {embeddingData.map((entry, index) => {
                      const colors = {
                        user: "#3b82f6",
                        inspiration: "#a855f7",
                        target: "#10b981",
                      };
                      return (
                        <Cell
                          key={`cell-${index}`}
                          fill={colors[entry.type as keyof typeof colors]}
                        />
                      );
                    })}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-6 flex items-center gap-6 text-sm relative z-10">
              <motion.div 
                className="flex items-center gap-2"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-neutral-600">User</span>
              </motion.div>
              <motion.div 
                className="flex items-center gap-2"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <div className="w-3 h-3 rounded-full bg-purple-500" />
                <span className="text-neutral-600">Inspiration</span>
              </motion.div>
              <AnimatePresence>
                {currentStep >= 3 && (
                  <motion.div 
                    className="flex items-center gap-2"
                    initial={{ opacity: 0, y: 10, scale: 0.8 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ 
                      duration: 0.3,
                      ease: [0.34, 1.56, 0.64, 1]
                    }}
                  >
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="text-neutral-600">Target</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <motion.p 
              className="mt-6 text-sm text-neutral-500 relative z-10"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              All style decisions are made in a shared embedding space.
            </motion.p>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}