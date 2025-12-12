"""
Test des stations reelles pour le scenario 4
Verifie la conversion GPS -> NED et la configuration des balises
"""

import numpy as np
from parametres import creer_stations_reelles, creer_stations_sol

def test_stations_reelles():
    """Test la creation des stations reelles"""
    
    print("="*70)
    print("TEST DES STATIONS REELLES POUR SCENARIO 4")
    print("="*70)
    
    # Creer les stations reelles
    stations_reelles = creer_stations_reelles()
    
    print(f"\n[OK] {len(stations_reelles)} stations reelles creees\n")
    
    # Afficher details de chaque station
    print("-"*70)
    print(f"{'Station':<10} {'Type':<10} {'N (m)':<12} {'E (m)':<12} {'h (m)':<10}")
    print("-"*70)
    
    for station in stations_reelles:
        # Determiner le type
        if station.a_vor and station.a_dme:
            type_station = "VOR/DME"
        elif station.a_vor:
            type_station = "VOR"
        elif station.a_dme:
            type_station = "DME"
        else:
            type_station = "Aucun"
        
        print(f"{station.nom:<10} {type_station:<10} {station.position[0]:>11.1f} {station.position[1]:>11.1f} {station.position[2]:>9.1f}")
    
    print("-"*70)
    
    # Statistiques
    print("\n[INFO] Statistiques des positions NED:")
    N_positions = [s.position[0] for s in stations_reelles]
    E_positions = [s.position[1] for s in stations_reelles]
    
    print(f"  Nord: min={min(N_positions):.1f}m, max={max(N_positions):.1f}m")
    print(f"  Est:  min={min(E_positions):.1f}m, max={max(E_positions):.1f}m")
    print(f"  Etendue N-S: {max(N_positions) - min(N_positions):.1f}m ({(max(N_positions) - min(N_positions))/1000:.1f}km)")
    print(f"  Etendue E-O: {max(E_positions) - min(E_positions):.1f}m ({(max(E_positions) - min(E_positions))/1000:.1f}km)")
    
    # Verifier capacites
    n_vor = sum(1 for s in stations_reelles if s.a_vor)
    n_dme = sum(1 for s in stations_reelles if s.a_dme)
    n_vordme = sum(1 for s in stations_reelles if s.a_vor and s.a_dme)
    
    print(f"\n[INFO] Capacites des stations:")
    print(f"  Stations VOR/DME: {n_vordme}")
    print(f"  Stations VOR seul: {n_vor - n_vordme}")
    print(f"  Stations DME seul: {n_dme - n_vordme}")
    print(f"  Total VOR: {n_vor}")
    print(f"  Total DME: {n_dme}")
    
    # Comparaison avec stations synthetiques
    print("\n" + "="*70)
    print("COMPARAISON AVEC STATIONS SYNTHETIQUES (scenarios 1-3)")
    print("="*70)
    
    stations_synth = creer_stations_sol()
    print(f"\nStations synthetiques: {len(stations_synth)}")
    print("-"*70)
    print(f"{'Station':<15} {'Type':<10} {'N (m)':<12} {'E (m)':<12} {'h (m)':<10}")
    print("-"*70)
    
    for station in stations_synth:
        type_station = "VOR/DME" if (station.a_vor and station.a_dme) else "?"
        print(f"{station.nom:<15} {type_station:<10} {station.position[0]:>11.1f} {station.position[1]:>11.1f} {station.position[2]:>9.1f}")
    
    print("-"*70)
    
    print("\n[SUCCESS] Test termine avec succes!")
    print("\nPour utiliser ces stations dans le scenario 4:")
    print("  1. Dans simulation_ins_vor_dme.ipynb, modifiez la cellule de selection du scenario")
    print("  2. Remplacez l'appel a creer_stations_sol() par creer_stations_reelles()")
    print("     pour le scenario 4 uniquement")
    
    return stations_reelles


if __name__ == "__main__":
    stations = test_stations_reelles()
