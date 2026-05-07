'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  FolderOpen, 
  FlaskConical, 
  BrainCircuit, 
  FileText, 
  Settings,
  Plus,
  Search,
  Bell,
  User
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderOpen },
  { name: 'Agents', href: '/agents', icon: BrainCircuit },
  { name: 'Experiments', href: '/experiments', icon: FlaskConical },
  { name: 'Knowledge', href: '/knowledge', icon: FileText },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="fixed inset-y-0 left-0 w-64 bg-dark-900 border-r border-dark-800">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center px-6 border-b border-dark-800">
          <BrainCircuit className="h-8 w-8 text-primary-500" />
          <span className="ml-3 text-lg font-bold text-white">Nexus OS</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors
                  ${isActive 
                    ? 'bg-primary-600 text-white' 
                    : 'text-dark-300 hover:bg-dark-800 hover:text-white'
                  }
                `}
              >
                <item.icon className={`mr-3 h-5 w-5 ${isActive ? 'text-white' : 'text-dark-400 group-hover:text-white'}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* New Project Button */}
        <div className="p-3 border-t border-dark-800">
          <Link
            href="/projects/new"
            className="flex w-full items-center justify-center px-4 py-2.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
          >
            <Plus className="mr-2 h-5 w-5" />
            New Project
          </Link>
        </div>

        {/* User Profile */}
        <div className="p-4 border-t border-dark-800">
          <div className="flex items-center">
            <div className="h-9 w-9 rounded-full bg-primary-600 flex items-center justify-center">
              <User className="h-5 w-5 text-white" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-white">Researcher</p>
              <p className="text-xs text-dark-400">Lab Admin</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function Header() {
  return (
    <header className="sticky top-0 z-40 bg-white/80 dark:bg-dark-900/80 backdrop-blur-md border-b border-dark-200">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Search */}
        <div className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-dark-400" />
            <input
              type="search"
              placeholder="Search projects, documents, agents..."
              className="w-full pl-10 pr-4 py-2 bg-dark-100 border border-dark-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          <button className="relative p-2 text-dark-400 hover:text-dark-600">
            <Bell className="h-6 w-6" />
            <span className="absolute top-1 right-1 h-2.5 w-2.5 bg-red-500 rounded-full border-2 border-white"></span>
          </button>
        </div>
      </div>
    </header>
  );
}
