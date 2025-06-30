import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { Users, Activity, TrendingUp, Pill, Calendar, AlertCircle, Loader2 } from 'lucide-react';
import { usePatients } from '@/hooks/usePatients';
import { useSpecialites } from '@/hooks/useSpecialites';

const AdminDashboard = () => {
  const { patients, loading: patientsLoading } = usePatients();
  const { specialites, loading: specialitesLoading } = useSpecialites();

  if (patientsLoading || specialitesLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Chargement du tableau de bord...</span>
      </div>
    );
  }

  // Statistiques générales
  const totalPatients = patients.length;
  const averageAge = patients.length > 0 ? 
    Math.round(patients.reduce((sum, p) => sum + p.age, 0) / patients.length) : 0;
  const averageIMC = patients.length > 0 ? 
    (patients.filter(p => p.imc > 0).reduce((sum, p) => sum + p.imc, 0) / patients.filter(p => p.imc > 0).length).toFixed(1) : '0';

  // Répartition par spécialité
  const specialityStats = patients.reduce((acc, patient) => {
    const spec = patient.specialite || 'Non spécifié';
    acc[spec] = (acc[spec] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const specialityData = Object.entries(specialityStats).map(([name, value]) => ({
    name,
    value,
    percentage: Math.round((value / totalPatients) * 100)
  }));

  // Répartition par tranche d'âge
  const ageGroups = patients.reduce((acc, patient) => {
    let group;
    if (patient.age < 18) group = '0-17 ans';
    else if (patient.age < 30) group = '18-29 ans';
    else if (patient.age < 50) group = '30-49 ans';
    else if (patient.age < 65) group = '50-64 ans';
    else group = '65+ ans';
    
    acc[group] = (acc[group] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const ageData = Object.entries(ageGroups).map(([name, value]) => ({
    name,
    patients: value
  }));

  // Analyse IMC
  const imcCategories = patients.filter(p => p.imc > 0).reduce((acc, patient) => {
    let category;
    if (patient.imc < 18.5) category = 'Insuffisant';
    else if (patient.imc < 25) category = 'Normal';
    else if (patient.imc < 30) category = 'Surpoids';
    else category = 'Obésité';
    
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const imcData = Object.entries(imcCategories).map(([name, value]) => ({
    name,
    patients: value
  }));

  // Médicaments les plus prescrits
  const medicamentStats = patients
    .filter(p => p.medicaments)
    .flatMap(p => p.medicaments.split(',').map(m => m.trim().toLowerCase()))
    .reduce((acc, med) => {
      if (med.length > 2) {
        acc[med] = (acc[med] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);

  const topMedicaments = Object.entries(medicamentStats)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10)
    .map(([name, count]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), count }));

  const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

  return (
    <div className="space-y-6">
      {/* Statistiques générales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-blue-200 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Patients</p>
                <p className="text-3xl font-bold text-blue-600">{totalPatients}</p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-200 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Âge Moyen</p>
                <p className="text-3xl font-bold text-green-600">{averageAge}</p>
                <p className="text-xs text-gray-500">ans</p>
              </div>
              <Calendar className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-orange-200 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">IMC Moyen</p>
                <p className="text-3xl font-bold text-orange-600">{averageIMC}</p>
                <p className="text-xs text-gray-500">kg/m²</p>
              </div>
              <Activity className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-purple-200 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Spécialités</p>
                <p className="text-3xl font-bold text-purple-600">{specialites.length}</p>
                <p className="text-xs text-gray-500">disponibles</p>
              </div>
              <Pill className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Répartition par spécialité */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <span>Répartition par Spécialité</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={specialityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name}: ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {specialityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Répartition par âge */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-green-600" />
              <span>Répartition par Âge</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ageData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="patients" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Analyse IMC */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-orange-600" />
              <span>Répartition IMC</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={imcData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="patients" fill="#F59E0B" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top médicaments */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Pill className="h-5 w-5 text-purple-600" />
              <span>Médicaments les Plus Prescrits</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topMedicaments.slice(0, 8).map((med, index) => (
                <div key={med.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                    <span className="text-sm font-medium">{med.name}</span>
                  </div>
                  <Badge variant="secondary">{med.count} patients</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alertes et recommandations */}
      <Card className="border-yellow-200 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-yellow-700">
            <AlertCircle className="h-5 w-5" />
            <span>Alertes et Recommandations</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {patients.filter(p => p.imc > 30).length > 0 && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">
                  <strong>{patients.filter(p => p.imc > 30).length} patient(s)</strong> présentent une obésité (IMC {"> "}30)
                </p>
              </div>
            )}
            
            {patients.filter(p => p.age > 65).length > 0 && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>{patients.filter(p => p.age > 65).length} patient(s)</strong> sont âgés de plus de 65 ans
                </p>
              </div>
            )}
            
            {patients.filter(p => !p.specialite).length > 0 && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>{patients.filter(p => !p.specialite).length} patient(s)</strong> n'ont pas de spécialité assignée
                </p>
              </div>
            )}

            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800">
                <strong>Base de données synchronisée:</strong> Toutes les modifications sont sauvegardées en temps réel et partagées avec tous les utilisateurs.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminDashboard;