
import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, UserPlus, BarChart3, Activity } from 'lucide-react';
import PatientForm from '@/components/PatientForm';
import PatientList from '@/components/PatientList';
import AdminDashboard from '@/components/AdminDashboard';

const Index = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Activity className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                Système de Gestion Patients
              </h1>
            </div>
            <div className="text-sm text-gray-500">
              Interface Médicale Professionnelle
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <Button
              variant={activeTab === 'dashboard' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('dashboard')}
              className="flex items-center space-x-2 py-4"
            >
              <BarChart3 className="h-4 w-4" />
              <span>Tableau de Bord</span>
            </Button>
            
            <Button
              variant={activeTab === 'form' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('form')}
              className="flex items-center space-x-2 py-4"
            >
              <UserPlus className="h-4 w-4" />
              <span>Nouveau Patient</span>
            </Button>
            
            <Button
              variant={activeTab === 'list' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('list')}
              className="flex items-center space-x-2 py-4"
            >
              <Users className="h-4 w-4" />
              <span>Liste des Patients</span>
            </Button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </main>
    </div>
  );
};

export default Index;
