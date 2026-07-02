import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppLayout } from "@/components/AppLayout";
import { LandingLayout } from "./components/LandingLayout";
import { LandingHome } from "./pages/LandingHome";
import { LandingTechnology } from "./pages/LandingTechnology";
import { LandingBacktesting } from "./pages/LandingBacktesting";
import { LandingPipeline } from "./pages/LandingPipeline";
import { LandingUseCases } from "./pages/LandingUseCases";
import Dashboard from "./pages/Dashboard";
import Matches from "./pages/Matches";
import MatchDetail from "./pages/MatchDetail";
import TeamProfile from "./pages/TeamProfile";
import PlayerProfile from "./pages/PlayerProfile";
import RefereeProfile from "./pages/RefereeProfile";
import History from "./pages/History";
import Predictor from "./pages/Predictor";
import Simulator from "./pages/Simulator";
import Jugar from "./pages/Jugar";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Landing page and subpages */}
          <Route element={<LandingLayout />}>
            <Route path="/" element={<LandingHome />} />
            <Route path="/technology" element={<LandingTechnology />} />
            <Route path="/backtesting" element={<LandingBacktesting />} />
            <Route path="/pipeline" element={<LandingPipeline />} />
            <Route path="/use-cases" element={<LandingUseCases />} />
          </Route>

          {/* App routes with sidebar */}
          <Route path="/dashboard" element={<AppLayout><Dashboard /></AppLayout>} />
          <Route path="/matches" element={<AppLayout><Matches /></AppLayout>} />
          <Route path="/match/:id" element={<AppLayout><MatchDetail /></AppLayout>} />
          <Route path="/performance" element={<Navigate to="/simulator" replace />} />
          <Route path="/predictor" element={<AppLayout><Predictor /></AppLayout>} />
          <Route path="/history" element={<AppLayout><History /></AppLayout>} />
          <Route path="/detailed-history" element={<Navigate to="/simulator" replace />} />
          <Route path="/simulator" element={<AppLayout><Simulator /></AppLayout>} />
          <Route path="/jugar" element={<AppLayout><Jugar /></AppLayout>} />
          <Route path="/team/:id" element={<AppLayout><TeamProfile /></AppLayout>} />
          <Route path="/player/:id" element={<AppLayout><PlayerProfile /></AppLayout>} />
          <Route path="/referee/:id" element={<AppLayout><RefereeProfile /></AppLayout>} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
