import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { TriangleAlert as AlertTriangle, Package, Plus, CreditCard as Edit, Trash2, Loader as Loader2, Pill, Heart, Search } from 'lucide-react';
import { useMedicaments } from '@/hooks/useMedicaments';
import type { Medicament, FamilleMedicament } from '@/types/database';

const PharmacyManagement = () => {
  const { medicaments, familles, loading, addMedicament, updateMedicament, updateStock, deleteMedicament, addFamille } = useMedicaments();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFamille, setSelectedFamille] = useState<string>('all');
  const [isAddingMedicament, setIsAddingMedicament] = useState(false);
  const [isAddingFamille, setIsAddingFamille] = useState(false);
  const [editingMedicament, setEditingMedicament] = useState<Medicament | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isAddMedicamentDialogOpen, setIsAddMedicamentDialogOpen] = useState(false);
  const [isAddFamilleDialogOpen, setIsAddFamilleDialogOpen] = useState(false);

  const [medicamentForm, setMedicamentForm] = useState({
    nom: '',
    famille_id: '',
    dosage: '',
    forme: '',
    stock_actuel: '',
    stock_minimum: '',
    prix_unitaire: '',
    description: ''
  });

  const [familleForm, setFamilleForm] = useState({
    nom: '',
    description: ''
  });

  const filteredMedicaments = medicaments.filter(medicament => {
    const matchesSearch = medicament.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         medicament.famille?.nom.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFamille = selectedFamille === 'all' || medicament.famille_id === selectedFamille;
    return matchesSearch && matchesFamille;
  });

  const medicamentsEnRupture = medicaments.filter(m => m.stock_actuel <= m.stock_minimum);

  const handleAddMedicament = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsAddingMedicament(true);
      await addMedicament({
        nom: medicamentForm.nom,
        famille_id: medicamentForm.famille_id,
        dosage: medicamentForm.dosage,
        forme: medicamentForm.forme,
        stock_actuel: parseInt(medicamentForm.stock_actuel) || 0,
        stock_minimum: parseInt(medicamentForm.stock_minimum) || 10,
        prix_unitaire: parseFloat(medicamentForm.prix_unitaire) || 0,
        description: medicamentForm.description
      });
      
      setMedicamentForm({
        nom: '', famille_id: '', dosage: '', forme: '', stock_actuel: '',
        stock_minimum: '', prix_unitaire: '', description: ''
      });
      setIsAddMedicamentDialogOpen(false);
    } catch (error) {
      // Error handled in hook
    } finally {
      setIsAddingMedicament(false);
    }
  };

  const handleEditMedicament = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingMedicament) return;

    try {
      setIsAddingMedicament(true);
      await updateMedicament(editingMedicament.id, {
        nom: medicamentForm.nom,
        famille_id: medicamentForm.famille_id,
        dosage: medicamentForm.dosage,
        forme: medicamentForm.forme,
        stock_actuel: parseInt(medicamentForm.stock_actuel) || 0,
        stock_minimum: parseInt(medicamentForm.stock_minimum) || 10,
        prix_unitaire: parseFloat(medicamentForm.prix_unitaire) || 0,
        description: medicamentForm.description
      });
      
      setIsEditDialogOpen(false);
      setEditingMedicament(null);
    } catch (error) {
      // Error handled in hook
    } finally {
      setIsAddingMedicament(false);
    }
  };

  const handleAddFamille = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsAddingFamille(true);
      await addFamille(familleForm.nom, familleForm.description);
      setFamilleForm({ nom: '', description: '' });
      setIsAddFamilleDialogOpen(false);
    } catch (error) {
      // Error handled in hook
    } finally {
      setIsAddingFamille(false);
    }
  };

  const openEditDialog = (medicament: Medicament) => {
    setEditingMedicament(medicament);
    setMedicamentForm({
      nom: medicament.nom,
      famille_id: medicament.famille_id,
      dosage: medicament.dosage,
      forme: medicament.forme,
      stock_actuel: medicament.stock_actuel.toString(),
      stock_minimum: medicament.stock_minimum.toString(),
      prix_unitaire: medicament.prix_unitaire.toString(),
      description: medicament.description
    });
    setIsEditDialogOpen(true);
  };

  const getStockStatus = (medicament: Medicament) => {
    if (medicament.stock_actuel === 0) {
      return { status: 'Rupture', color: 'bg-red-100 text-red-800 border-red-200' };
    } else if (medicament.stock_actuel <= medicament.stock_minimum) {
      return { status: 'Stock faible', color: 'bg-orange-100 text-orange-800 border-orange-200' };
    } else {
      return { status: 'En stock', color: 'bg-green-100 text-green-800 border-green-200' };
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2 text-gray-600">Chargement de la pharmacie...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* En-tête */}
      <Card className="border-primary/20 shadow-xl card-hover">
        <CardHeader className="medical-gradient text-white">
          <CardTitle className="flex items-center space-x-3">
            <img 
              src="/2.png" 
              alt="PAR'ACT Logo" 
              className="h-8 w-8 object-contain bg-white rounded-full p-1"
            />
            <Heart className="h-6 w-6 animate-pulse-slow" />
            <Package className="h-6 w-6" />
            <span>Gestion de la Pharmacie</span>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Alertes de stock */}
      {medicamentsEnRupture.length > 0 && (
        <Card className="border-red-200 shadow-lg animate-slide-in-left">
          <CardHeader className="bg-red-50">
            <CardTitle className="flex items-center space-x-2 text-red-700">
              <AlertTriangle className="h-5 w-5" />
              <span>Alertes de Stock ({medicamentsEnRupture.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {medicamentsEnRupture.map((medicament) => (
                <div key={medicament.id} className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div>
                    <p className="font-medium text-red-800">{medicament.nom}</p>
                    <p className="text-sm text-red-600">Stock: {medicament.stock_actuel}</p>
                  </div>
                  <Badge className="bg-red-100 text-red-800">
                    {medicament.stock_actuel === 0 ? 'Rupture' : 'Stock faible'}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="medicaments" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="medicaments">Médicaments</TabsTrigger>
          <TabsTrigger value="familles">Familles de Médicaments</TabsTrigger>
        </TabsList>

        <TabsContent value="medicaments" className="space-y-6">
          {/* Filtres et recherche */}
          <Card className="shadow-lg">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-4 items-end">
                <div className="flex-1">
                  <Label htmlFor="search">Rechercher un médicament</Label>
                  <div className="relative mt-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="search"
                      placeholder="Nom du médicament ou famille..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <div className="min-w-[200px]">
                  <Label>Filtrer par famille</Label>
                  <Select value={selectedFamille} onValueChange={setSelectedFamille}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Toutes les familles</SelectItem>
                      {familles.map((famille) => (
                        <SelectItem key={famille.id} value={famille.id}>
                          {famille.nom}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Dialog open={isAddMedicamentDialogOpen} onOpenChange={setIsAddMedicamentDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="bg-green-500 hover:bg-green-600">
                      <Plus className="h-4 w-4 mr-2" />
                      Nouveau Médicament
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Ajouter un nouveau médicament</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleAddMedicament} className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="nom">Nom du médicament *</Label>
                          <Input
                            id="nom"
                            value={medicamentForm.nom}
                            onChange={(e) => setMedicamentForm(prev => ({ ...prev, nom: e.target.value }))}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="famille">Famille *</Label>
                          <Select 
                            value={medicamentForm.famille_id} 
                            onValueChange={(value) => setMedicamentForm(prev => ({ ...prev, famille_id: value }))}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Sélectionner une famille" />
                            </SelectTrigger>
                            <SelectContent>
                              {familles.map((famille) => (
                                <SelectItem key={famille.id} value={famille.id}>
                                  {famille.nom}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="dosage">Dosage</Label>
                          <Input
                            id="dosage"
                            value={medicamentForm.dosage}
                            onChange={(e) => setMedicamentForm(prev => ({ ...prev, dosage: e.target.value }))}
                            placeholder="ex: 500mg"
                          />
                        </div>
                        <div>
                          <Label htmlFor="forme">Forme galénique</Label>
                          <Input
                            id="forme"
                            value={medicamentForm.forme}
                            onChange={(e) => setMedicamentForm(prev => ({ ...prev, forme: e.target.value }))}
                            placeholder="ex: Comprimé, Sirop"
                          />
                        </div>
                        <div>
                          <Label htmlFor="stock_actuel">Stock actuel</Label>
                          <Input
                            id="stock_actuel"
                            type="number"
                            value={medicamentForm.stock_actuel}
                            onChange={(e) => setMedicamentForm(prev => ({ ...prev, stock_actuel: e.target.value }))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="stock_minimum">Stock minimum</Label>
                          <Input
                            id="stock_minimum"
                            type="number"
                            value={medicamentForm.stock_minimum}
                            onChange={(e) => setMedicamentForm(prev => ({ ...prev, stock_minimum: e.target.value }))}
                          />
                        </div>
                        <div className="md:col-span-2">
                          <Label htmlFor="prix_unitaire">Prix unitaire (€)</Label>
                          <Input
                            id="prix_unitaire"
                            type="number"
                            step="0.01"
                            value={medicamentForm.prix_unitaire}
                            onChange={(e) => setMedicamentForm(prev => ({ ...prev, prix_unitaire: e.target.value }))}
                          />
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="description">Description/Indications</Label>
                        <Textarea
                          id="description"
                          value={medicamentForm.description}
                          onChange={(e) => setMedicamentForm(prev => ({ ...prev, description: e.target.value }))}
                          rows={3}
                        />
                      </div>
                      <div className="flex gap-3">
                        <Button type="submit" disabled={isAddingMedicament} className="flex-1">
                          {isAddingMedicament ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Ajout en cours...
                            </>
                          ) : (
                            'Ajouter le médicament'
                          )}
                        </Button>
                        <Button type="button" variant="outline" onClick={() => setIsAddMedicamentDialogOpen(false)}>
                          Annuler
                        </Button>
                      </div>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardContent>
          </Card>

          {/* Liste des médicaments */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredMedicaments.map((medicament, index) => {
              const stockStatus = getStockStatus(medicament);
              return (
                <Card key={medicament.id} className={`shadow-lg card-hover animate-fade-in-up delay-${100 + index * 50}`}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{medicament.nom}</CardTitle>
                        <p className="text-sm text-gray-600 mt-1">
                          {medicament.famille?.nom} • {medicament.dosage} {medicament.forme}
                        </p>
                      </div>
                      <Badge className={stockStatus.color}>
                        {stockStatus.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Stock:</span>
                        <p className="text-lg font-bold text-primary">{medicament.stock_actuel}</p>
                      </div>
                      <div>
                        <span className="font-medium">Prix:</span>
                        <p className="text-lg font-bold text-green-600">{medicament.prix_unitaire}€</p>
                      </div>
                    </div>
                    
                    {medicament.description && (
                      <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        {medicament.description}
                      </p>
                    )}

                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openEditDialog(medicament)}
                        className="flex-1"
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Modifier
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deleteMedicament(medicament.id)}
                        className="text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {filteredMedicaments.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Aucun médicament trouvé
            </div>
          )}
        </TabsContent>

        <TabsContent value="familles" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Familles de Médicaments</h2>
            <Dialog open={isAddFamilleDialogOpen} onOpenChange={setIsAddFamilleDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-500 hover:bg-blue-600">
                  <Plus className="h-4 w-4 mr-2" />
                  Nouvelle Famille
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Ajouter une nouvelle famille</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleAddFamille} className="space-y-4">
                  <div>
                    <Label htmlFor="famille_nom">Nom de la famille *</Label>
                    <Input
                      id="famille_nom"
                      value={familleForm.nom}
                      onChange={(e) => setFamilleForm(prev => ({ ...prev, nom: e.target.value }))}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="famille_description">Description</Label>
                    <Textarea
                      id="famille_description"
                      value={familleForm.description}
                      onChange={(e) => setFamilleForm(prev => ({ ...prev, description: e.target.value }))}
                      rows={3}
                    />
                  </div>
                  <div className="flex gap-3">
                    <Button type="submit" disabled={isAddingFamille} className="flex-1">
                      {isAddingFamille ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Ajout en cours...
                        </>
                      ) : (
                        'Ajouter la famille'
                      )}
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setIsAddFamilleDialogOpen(false)}>
                      Annuler
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {familles.map((famille, index) => (
              <Card key={famille.id} className={`shadow-lg card-hover animate-fade-in-up delay-${100 + index * 50}`}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Pill className="h-5 w-5 text-primary" />
                    <span>{famille.nom}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {famille.description && (
                    <p className="text-gray-600 mb-3">{famille.description}</p>
                  )}
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary">
                      {famille.medicaments?.length || 0} médicament(s)
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Dialog d'édition */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Modifier le médicament</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEditMedicament} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_nom">Nom du médicament *</Label>
                <Input
                  id="edit_nom"
                  value={medicamentForm.nom}
                  onChange={(e) => setMedicamentForm(prev => ({ ...prev, nom: e.target.value }))}
                  required
                />
              </div>
              <div>
                <Label htmlFor="edit_famille">Famille *</Label>
                <Select 
                  value={medicamentForm.famille_id} 
                  onValueChange={(value) => setMedicamentForm(prev => ({ ...prev, famille_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {familles.map((famille) => (
                      <SelectItem key={famille.id} value={famille.id}>
                        {famille.nom}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="edit_dosage">Dosage</Label>
                <Input
                  id="edit_dosage"
                  value={medicamentForm.dosage}
                  onChange={(e) => setMedicamentForm(prev => ({ ...prev, dosage: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="edit_forme">Forme galénique</Label>
                <Input
                  id="edit_forme"
                  value={medicamentForm.forme}
                  onChange={(e) => setMedicamentForm(prev => ({ ...prev, forme: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="edit_stock_actuel">Stock actuel</Label>
                <Input
                  id="edit_stock_actuel"
                  type="number"
                  value={medicamentForm.stock_actuel}
                  onChange={(e) => setMedicamentForm(prev => ({ ...prev, stock_actuel: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="edit_stock_minimum">Stock minimum</Label>
                <Input
                  id="edit_stock_minimum"
                  type="number"
                  value={medicamentForm.stock_minimum}
                  onChange={(e) => setMedicamentForm(prev => ({ ...prev, stock_minimum: e.target.value }))}
                />
              </div>
              <div className="md:col-span-2">
                <Label htmlFor="edit_prix_unitaire">Prix unitaire (€)</Label>
                <Input
                  id="edit_prix_unitaire"
                  type="number"
                  step="0.01"
                  value={medicamentForm.prix_unitaire}
                  onChange={(e) => setMedicamentForm(prev => ({ ...prev, prix_unitaire: e.target.value }))}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="edit_description">Description/Indications</Label>
              <Textarea
                id="edit_description"
                value={medicamentForm.description}
                onChange={(e) => setMedicamentForm(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
              />
            </div>
            <div className="flex gap-3">
              <Button type="submit" disabled={isAddingMedicament} className="flex-1">
                {isAddingMedicament ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Modification en cours...
                  </>
                ) : (
                  'Sauvegarder les modifications'
                )}
              </Button>
              <Button type="button" variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                Annuler
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PharmacyManagement;