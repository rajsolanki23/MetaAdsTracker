import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useSearchParams } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from './components/ui/Toast';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { Navbar } from './components/layout/Navbar';
import { LeaderboardPage } from './pages/LeaderboardPage';
import { ClientsPage } from './pages/ClientsPage';
import { CreativeDetailPage } from './pages/CreativeDetailPage';
import { MetaSyncPage } from './pages/MetaSyncPage';
import { ClientSettingsPage } from './pages/ClientSettingsPage';
import { BulkImportModal } from './components/import/BulkImportModal';
import { useClients } from './api/queries';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 15000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const DashboardLayout: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { data: clients = [] } = useClients();

  const selectedClientId = searchParams.get('client_id') || '';
  const [isBulkImportOpen, setIsBulkImportOpen] = useState(false);

  const handleSelectClient = (id: string) => {
    if (id) {
      setSearchParams({ client_id: id });
    } else {
      setSearchParams({});
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col">
      <Navbar
        selectedClientId={selectedClientId}
        onSelectClient={handleSelectClient}
        onOpenBulkImport={() => setIsBulkImportOpen(true)}
      />

      <main className="flex-1">
        <Routes>
          <Route path="/" element={<LeaderboardPage />} />
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/creatives/:id" element={<CreativeDetailPage />} />
          <Route path="/sync" element={<MetaSyncPage />} />
          <Route path="/settings" element={<ClientSettingsPage />} />
        </Routes>
      </main>

      <footer className="border-t border-slate-800/80 py-4 bg-[#090d16]/90 text-center text-xs text-slate-500 font-mono">
        <div className="max-w-[1600px] mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Creative Leaderboard © 2026 • 100% Open Source ($0/mo Stack)</span>
          <span className="text-[11px] text-slate-600">FastAPI + Motor MongoDB + React Vite + Meta Marketing API v18.0</span>
        </div>
      </footer>

      <BulkImportModal
        isOpen={isBulkImportOpen}
        onClose={() => setIsBulkImportOpen(false)}
        clients={clients}
        defaultClientId={selectedClientId}
      />
    </div>
  );
};

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <DashboardLayout />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </QueryClientProvider>
  );
}

export default App;
