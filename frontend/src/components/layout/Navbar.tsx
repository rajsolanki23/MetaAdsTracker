import React from 'react';
import { NavLink } from 'react-router-dom';
import { Trophy, LayoutGrid, RefreshCw, Settings, Upload, Flame, ChevronDown } from 'lucide-react';
import { useClients, useTriggerAllSync } from '../../api/queries';
import { useToast } from '../ui/Toast';
import { Button } from '../ui/Button';

interface NavbarProps {
  selectedClientId?: string;
  onSelectClient?: (clientId: string) => void;
  onOpenBulkImport?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  selectedClientId,
  onSelectClient,
  onOpenBulkImport,
}) => {
  const { data: clients = [] } = useClients();
  const triggerAllSync = useTriggerAllSync();
  const { showToast } = useToast();

  const handleSyncAll = async () => {
    try {
      showToast('Triggering Meta sync for all active accounts...', 'info');
      const res = await triggerAllSync.mutateAsync();
      showToast(`Sync complete! ${res.total_clients} accounts updated.`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Sync failed', 'error');
    }
  };

  const navLinks = [
    { to: '/', label: 'Leaderboard', icon: Trophy },
    { to: '/clients', label: 'Client View', icon: LayoutGrid },
    { to: '/sync', label: 'Meta Sync', icon: RefreshCw },
    { to: '/settings', label: 'Client Settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-40 w-full bg-[#090d16]/95 border-b border-slate-800/80 backdrop-blur-md">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Brand & Navigation */}
        <div className="flex items-center gap-8">
          <NavLink to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-400 via-orange-500 to-rose-500 p-0.5 shadow-[0_0_15px_rgba(245,158,11,0.4)] group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-[#090d16] rounded-[10px] flex items-center justify-center">
                <Flame className="w-5 h-5 text-amber-400 animate-pulse-flame" />
              </div>
            </div>
            <div>
              <span className="text-base font-extrabold tracking-tight text-white flex items-center gap-1.5 font-mono">
                CREATIVE<span className="text-amber-400">LEADERBOARD</span>
              </span>
              <span className="block text-[10px] font-semibold text-slate-400 tracking-wider uppercase -mt-0.5">
                Performance Marketing
              </span>
            </div>
          </NavLink>

          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                      isActive
                        ? 'bg-slate-800 text-amber-400 border border-slate-700 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`
                  }
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{link.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Right: Client Filter & Action Buttons */}
        <div className="flex items-center gap-3">
          {onSelectClient && (
            <div className="relative min-w-[170px]">
              <select
                value={selectedClientId || ''}
                onChange={(e) => onSelectClient(e.target.value)}
                className="w-full pl-3 pr-8 py-1.5 bg-slate-900 border border-slate-700/80 rounded-lg text-xs font-semibold text-slate-200 focus:outline-none focus:border-amber-400 appearance-none cursor-pointer"
              >
                <option value="">All Client Accounts</option>
                {clients.map((c) => (
                  <option key={c._id} value={c._id}>
                    {c.name} ({c.currency})
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          )}

          {onOpenBulkImport && (
            <Button
              variant="outline"
              size="sm"
              onClick={onOpenBulkImport}
              className="border-slate-700 hover:border-slate-600 text-xs"
            >
              <Upload className="w-3.5 h-3.5 mr-1" />
              <span>Bulk Paste</span>
            </Button>
          )}

          <Button
            variant="primary"
            size="sm"
            onClick={handleSyncAll}
            isLoading={triggerAllSync.isPending}
            className="text-xs"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            <span>Sync All</span>
          </Button>
        </div>
      </div>
    </header>
  );
};
