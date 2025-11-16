import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, UserPlus, BarChart3, Activity, Heart, Package } from 'lucide-react';
import PatientForm from '@/components/PatientForm';
import PatientList from '@/components/PatientList';
import AdminDashboard from '@/components/AdminDashboard';

const Index = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Animation d'entrée après le chargement du composant
    const timer = setTimeout(() => {
      setIsLoaded(true);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'form':
        return <PatientForm />;
      case 'list':
        return <PatientList />;
      case 'dashboard':
        return <AdminDashboard />;
      default:
        return <AdminDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-red-25">
      {/* Header avec animations */}
      <header className={`bg-white shadow-lg border-b border-red-100 ${isLoaded ? 'animate-slide-in-left' : 'opacity-0'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-4">
              {/* Nouveau logo PAR'ACT avec animation */}
              <div className={`${isLoaded ? 'animate-scale-in delay-200' : 'opacity-0'}`}>
                <img 
                  src="/2.png" 
                  alt="PAR'ACT Association Logo" 
                  className="h-14 w-14 object-contain animate-heartbeat"
                />
              </div>
              
              {/* Icône médicale avec animation */}
              <div className={`${isLoaded ? 'animate-scale-in delay-300' : 'opacity-0'}`}>
                <Heart className="h-8 w-8 text-primary animate-pulse-slow" />
              </div>
              
              {/* Titre avec animation */}
              <div className={`${isLoaded ? 'animate-fade-in-up delay-400' : 'opacity-0'}`}>
                <h1 className="text-2xl font-bold text-gray-900">
                  Système de Gestion Patients
                </h1>
                <p className="text-sm text-primary font-medium">PAR'ACT Association</p>
              </div>
            </div>
            
            {/* Badge professionnel avec animation */}
            <div className={`${isLoaded ? 'animate-slide-in-right delay-500' : 'opacity-0'}`}>
              <div className="bg-gradient-to-r from-primary to-red-600 text-white px-4 py-2 rounded-full shadow-lg">
                <div className="text-sm font-semibold">Interface Médicale</div>
                <div className="text-xs opacity-90">Professionnelle</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation avec animations */}
      <nav className={`bg-white border-b border-red-100 shadow-sm ${isLoaded ? 'animate-fade-in-up delay-300' : 'opacity-0'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <Button
              variant={activeTab === 'dashboard' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center space-x-2 py-4 smooth-transition ${
                activeTab === 'dashboard' 
                  ? 'bg-primary hover:bg-primary/90 text-white shadow-lg' 
                  : 'hover:bg-red-50 hover:text-primary'
              }`}
            >
              <BarChart3 className="h-4 w-4" />
              <span>Tableau de Bord</span>
            </Button>
            
            <Button
              variant={activeTab === 'form' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('form')}
              className={`flex items-center space-x-2 py-4 smooth-transition ${
                activeTab === 'form' 
                  ? 'bg-primary hover:bg-primary/90 text-white shadow-lg' 
                  : 'hover:bg-red-50 hover:text-primary'
              }`}
            >
              <UserPlus className="h-4 w-4" />
              <span>Nouveau Patient</span>
            </Button>
            
            <Button
              variant={activeTab === 'list' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('list')}
              className={`flex items-center space-x-2 py-4 smooth-transition ${
                activeTab === 'list' 
                  ? 'bg-primary hover:bg-primary/90 text-white shadow-lg' 
                  : 'hover:bg-red-50 hover:text-primary'
              }`}
            >
              <Users className="h-4 w-4" />
              <span>Liste des Patients</span>
            </Button>
          </div>
        </div>
      </nav>

      {/* Main Content avec animation */}
      <main className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 ${isLoaded ? 'animate-fade-in-up delay-600' : 'opacity-0'}`}>
        <div className="transition-all duration-500 ease-in-out">
          {renderContent()}
        </div>
      </main>

      {/* Footer avec logo et informations */}
      <footer className={`bg-white border-t border-red-100 mt-16 ${isLoaded ? 'animate-fade-in-up delay-700' : 'opacity-0'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img 
                src="/2.png" 
                alt="PAR'ACT Association" 
                className="h-8 w-8 object-contain"
              />
              <div className="text-sm text-gray-600">
                <div className="font-semibold">PAR'ACT Association</div>
                <div>Système de Gestion Médicale</div>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              © 2025 PAR'ACT Association. Tous droits réservés.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;