"""
Module de visualisation des resultats

Contient les fonctions de plot et d'animation.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Ellipse
import matplotlib as mpl


def plot_trajectoires_2D(verite, traj_ins, traj_ekf, stations):
    """
    Plot des trajectoires 2D (vue de dessus)
    
    Parametres:
    -----------
    verite : dict
        Trajectoire verite
    traj_ins : dict
        Trajectoire INS seule
    traj_ekf : dict
        Trajectoire INS + EKF
    stations : list[Station]
        Liste des stations
    
    Retour:
    -------
    fig, ax
        Figure et axes matplotlib
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Trajectoires avec marqueurs
    # Sous-echantillonnage pour marqueurs (tous les 10000 points)
    step = 10000
    
    # Verite avec marqueurs x
    ax.plot(verite['E'] / 1000.0, verite['N'] / 1000.0, 
            'k-x', linewidth=2, markersize=8, markevery=step, 
            markeredgewidth=2, label='Verite')
    
    # INS seule
    ax.plot(traj_ins['E'] / 1000.0, traj_ins['N'] / 1000.0, 
            'r--', linewidth=1.5, label='INS seule')
    
    # INS + EKF avec marqueurs o
    ax.plot(traj_ekf['E'] / 1000.0, traj_ekf['N'] / 1000.0, 
            'b-o', linewidth=1.5, markersize=6, markevery=step,
            markerfacecolor='none', markeredgewidth=1.5, label='INS + Kalman (EKF ou CMKF ou IMM)')
    
    # Stations
    for station in stations:
        ax.plot(station.position[1] / 1000.0, station.position[0] / 1000.0,
                '^g', markersize=15, markeredgecolor='black', markeredgewidth=1.5)
        ax.text(station.position[1] / 1000.0, station.position[0] / 1000.0 + 3,
                station.nom, ha='center', fontsize=10, fontweight='bold')
    
    # Calcul limites axes incluant trajectoires ET stations
    all_N = np.concatenate([verite['N'], traj_ins['N'], traj_ekf['N']])
    all_E = np.concatenate([verite['E'], traj_ins['E'], traj_ekf['E']])
    
    stations_N = np.array([s.position[0] for s in stations])
    stations_E = np.array([s.position[1] for s in stations])
    
    all_N = np.concatenate([all_N, stations_N])
    all_E = np.concatenate([all_E, stations_E])
    
    margin = 0.1
    N_range = all_N.max() - all_N.min()
    E_range = all_E.max() - all_E.min()
    
    ax.set_xlim((all_E.min() - margin * E_range) / 1000.0,
                (all_E.max() + margin * E_range) / 1000.0)
    ax.set_ylim((all_N.min() - margin * N_range) / 1000.0,
                (all_N.max() + margin * N_range) / 1000.0)
    
    ax.set_xlabel('Est (km)', fontsize=12)
    ax.set_ylabel('Nord (km)', fontsize=12)
    ax.set_title('Trajectoires 2D', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='datalim')
    
    return fig, ax


def plot_erreurs_temporelles(t, erreurs_ins, erreurs_ekf, nom_filtre='EKF'):
    """
    Plot des erreurs temporelles
    
    Parametres:
    -----------
    t : np.ndarray
        Temps (s)
    erreurs_ins : dict
        Erreurs INS seule
    erreurs_ekf : dict
        Erreurs INS + filtre
    nom_filtre : str
        Nom du filtre ('EKF' ou 'CMKF')
    
    Retour:
    -------
    fig
        Figure matplotlib
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # Erreur Nord
    axes[0].plot(t / 60.0, erreurs_ins['err_N'], 'r-', linewidth=1, label='INS seule')
    axes[0].plot(t / 60.0, erreurs_ekf['err_N'], 'b-', linewidth=1, label='INS + EKF')
    axes[0].set_ylabel('Erreur Nord (m)', fontsize=11)
    axes[0].set_title('Erreurs de position temporelles', fontsize=13, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # Erreur Est
    axes[1].plot(t / 60.0, erreurs_ins['err_E'], 'r-', linewidth=1, label='INS seule')
    axes[1].plot(t / 60.0, erreurs_ekf['err_E'], 'b-', linewidth=1, label='INS + EKF')
    axes[1].set_ylabel('Erreur Est (m)', fontsize=11)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    # Erreur 2D
    axes[2].plot(t / 60.0, erreurs_ins['err_2D'], 'r-', linewidth=1, label='INS seule')
    axes[2].plot(t / 60.0, erreurs_ekf['err_2D'], 'b-', linewidth=1, label='INS + EKF')
    axes[2].set_xlabel('Temps (min)', fontsize=11)
    axes[2].set_ylabel('Erreur 2D (m)', fontsize=11)
    axes[2].legend(fontsize=10)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return fig


def plot_rmse_glissant(t, rmse_ins, rmse_ekf, fenetre_s):
    """
    Plot du RMSE glissant
    
    Parametres:
    -----------
    t : np.ndarray
        Temps (s)
    rmse_ins : dict
        RMSE glissant INS avec cles 'N', 'E', '2D'
    rmse_ekf : dict
        RMSE glissant EKF avec cles 'N', 'E', '2D'
    fenetre_s : float
        Largeur fenetre (s)
    
    Retour:
    -------
    fig
        Figure matplotlib
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    titre = f'RMSE glissant (fenetre {fenetre_s:.0f}s)'
    
    # RMSE Nord
    axes[0].plot(t / 60.0, rmse_ins['N'], 'r-', linewidth=1.5, label='INS seule')
    axes[0].plot(t / 60.0, rmse_ekf['N'], 'b-', linewidth=1.5, label='INS + EKF')
    axes[0].set_ylabel('RMSE Nord (m)', fontsize=11)
    axes[0].set_title(titre, fontsize=13, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # RMSE Est
    axes[1].plot(t / 60.0, rmse_ins['E'], 'r-', linewidth=1.5, label='INS seule')
    axes[1].plot(t / 60.0, rmse_ekf['E'], 'b-', linewidth=1.5, label='INS + EKF')
    axes[1].set_ylabel('RMSE Est (m)', fontsize=11)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    # RMSE 2D
    axes[2].plot(t / 60.0, rmse_ins['2D'], 'r-', linewidth=1.5, label='INS seule')
    axes[2].plot(t / 60.0, rmse_ekf['2D'], 'b-', linewidth=1.5, label='INS + EKF')
    axes[2].set_xlabel('Temps (min)', fontsize=11)
    axes[2].set_ylabel('RMSE 2D (m)', fontsize=11)
    axes[2].legend(fontsize=10)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return fig


def plot_innovations_ekf(historique_ekf):
    """
    Plot des innovations EKF
    
    Parametres:
    -----------
    historique_ekf : dict
        Historique EKF
    
    Retour:
    -------
    fig
        Figure matplotlib
    """
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    
    # Innovations VOR
    if len(historique_ekf['innovations_vor']) > 0:
        innov_vor = np.array(historique_ekf['innovations_vor'])
        gating_vor = np.array(historique_ekf['gating_vor'])
        
        # Indices mesures acceptees/rejetees
        idx_accepte = gating_vor <= 9.21
        idx_rejete = gating_vor > 9.21
        
        if np.any(idx_accepte):
            axes[0].scatter(np.arange(len(innov_vor))[idx_accepte], 
                          np.rad2deg(innov_vor[idx_accepte]),
                          c='blue', s=20, alpha=0.6, label='Accepte')
        if np.any(idx_rejete):
            axes[0].scatter(np.arange(len(innov_vor))[idx_rejete], 
                          np.rad2deg(innov_vor[idx_rejete]),
                          c='red', s=20, alpha=0.6, label='Rejete')
        
        axes[0].axhline(0, color='k', linestyle='--', linewidth=0.8)
        axes[0].set_ylabel('Innovation VOR (deg)', fontsize=11)
        axes[0].set_title('Innovations EKF', fontsize=13, fontweight='bold')
        axes[0].legend(fontsize=10)
        axes[0].grid(True, alpha=0.3)
    
    # Innovations DME
    if len(historique_ekf['innovations_dme']) > 0:
        innov_dme = np.array(historique_ekf['innovations_dme'])
        gating_dme = np.array(historique_ekf['gating_dme'])
        
        idx_accepte = gating_dme <= 9.21
        idx_rejete = gating_dme > 9.21
        
        if np.any(idx_accepte):
            axes[1].scatter(np.arange(len(innov_dme))[idx_accepte], 
                          innov_dme[idx_accepte],
                          c='blue', s=20, alpha=0.6, label='Accepte')
        if np.any(idx_rejete):
            axes[1].scatter(np.arange(len(innov_dme))[idx_rejete], 
                          innov_dme[idx_rejete],
                          c='red', s=20, alpha=0.6, label='Rejete')
        
        axes[1].axhline(0, color='k', linestyle='--', linewidth=0.8)
        axes[1].set_xlabel('Numero mesure', fontsize=11)
        axes[1].set_ylabel('Innovation DME (m)', fontsize=11)
        axes[1].legend(fontsize=10)
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return fig


def plot_covariance_ekf(historique_ekf):
    """
    Plot de l'evolution de la covariance EKF
    
    Parametres:
    -----------
    historique_ekf : dict
        Historique EKF
    
    Retour:
    -------
    fig
        Figure matplotlib
    """
    if len(historique_ekf['t']) == 0:
        return None
    
    t = np.array(historique_ekf['t'])
    P_list = historique_ekf['P']
    
    # Extraction ecarts-types position
    sigma_N = np.array([np.sqrt(P[0, 0]) for P in P_list])
    sigma_E = np.array([np.sqrt(P[1, 1]) for P in P_list])
    sigma_h = np.array([np.sqrt(P[2, 2]) for P in P_list])
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # Ecart-type Nord
    axes[0].plot(t / 60.0, sigma_N, 'b-', linewidth=1.5)
    axes[0].set_ylabel('Ecart-type Nord (m)', fontsize=11)
    axes[0].set_title('Evolution incertitude EKF', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Ecart-type Est
    axes[1].plot(t / 60.0, sigma_E, 'b-', linewidth=1.5)
    axes[1].set_ylabel('Ecart-type Est (m)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    # Ecart-type altitude
    axes[2].plot(t / 60.0, sigma_h, 'b-', linewidth=1.5)
    axes[2].set_xlabel('Temps (min)', fontsize=11)
    axes[2].set_ylabel('Ecart-type altitude (m)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return fig


def animer_trajectoires(verite, traj_ins, traj_ekf, stations, vitesse_lecture=200):
    """
    Animation des trajectoires
    
    Parametres:
    -----------
    verite : dict
        Trajectoire verite
    traj_ins : dict
        Trajectoire INS seule
    traj_ekf : dict
        Trajectoire INS + EKF
    stations : list[Station]
        Liste des stations
    vitesse_lecture : float
        Facteur acceleration (200 = x200 plus rapide par defaut)
    
    Retour:
    -------
    FuncAnimation
        Animation matplotlib
    """
    mpl.rcParams['animation.embed_limit'] = 200
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=80)
    
    # Configuration axes
    ax.set_xlabel('Est (km)', fontsize=12)
    ax.set_ylabel('Nord (km)', fontsize=12)
    ax.set_title('Animation trajectoires', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Stations
    for station in stations:
        ax.plot(station.position[1] / 1000.0, station.position[0] / 1000.0,
                '^g', markersize=15, markeredgecolor='black', markeredgewidth=1.5)
        ax.text(station.position[1] / 1000.0, station.position[0] / 1000.0 + 3,
                station.nom, ha='center', fontsize=10, fontweight='bold')
    
    # Lignes trajectoires
    line_verite, = ax.plot([], [], 'k-', linewidth=2, label='Verite')
    line_ins, = ax.plot([], [], 'r--', linewidth=1.5, label='INS seule')
    line_ekf, = ax.plot([], [], 'b-', linewidth=1.5, label='INS + EKF')
    
    # Marqueurs position courante
    marker_verite, = ax.plot([], [], 'ko', markersize=8)
    marker_ins, = ax.plot([], [], 'ro', markersize=8)
    marker_ekf, = ax.plot([], [], 'bo', markersize=8)
    
    # Texte temps
    text_temps = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                        fontsize=12, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.legend(fontsize=11)
    
    # Calcul limites axes incluant trajectoires ET stations
    all_N = np.concatenate([verite['N'], traj_ins['N'], traj_ekf['N']])
    all_E = np.concatenate([verite['E'], traj_ins['E'], traj_ekf['E']])
    
    stations_N = np.array([s.position[0] for s in stations])
    stations_E = np.array([s.position[1] for s in stations])
    
    all_N = np.concatenate([all_N, stations_N])
    all_E = np.concatenate([all_E, stations_E])
    
    margin = 0.1
    N_range = all_N.max() - all_N.min()
    E_range = all_E.max() - all_E.min()
    
    ax.set_xlim((all_E.min() - margin * E_range) / 1000.0,
                (all_E.max() + margin * E_range) / 1000.0)
    ax.set_ylim((all_N.min() - margin * N_range) / 1000.0,
                (all_N.max() + margin * N_range) / 1000.0)
    ax.set_aspect('equal', adjustable='datalim')
    
    # Fonction d'initialisation
    def init():
        line_verite.set_data([], [])
        line_ins.set_data([], [])
        line_ekf.set_data([], [])
        marker_verite.set_data([], [])
        marker_ins.set_data([], [])
        marker_ekf.set_data([], [])
        text_temps.set_text('')
        return line_verite, line_ins, line_ekf, marker_verite, marker_ins, marker_ekf, text_temps
    
    # Fonction d'animation
    def animate(frame):
        idx = frame * vitesse_lecture
        if idx >= len(verite['t']):
            idx = len(verite['t']) - 1
        
        # Assurer au moins 1 point pour affichage
        idx_plot = max(1, idx)
        
        # Trajectoires jusqu'a l'instant courant
        line_verite.set_data(verite['E'][:idx_plot] / 1000.0, verite['N'][:idx_plot] / 1000.0)
        line_ins.set_data(traj_ins['E'][:idx_plot] / 1000.0, traj_ins['N'][:idx_plot] / 1000.0)
        line_ekf.set_data(traj_ekf['E'][:idx_plot] / 1000.0, traj_ekf['N'][:idx_plot] / 1000.0)
        
        # Positions courantes
        marker_verite.set_data([verite['E'][idx] / 1000.0], [verite['N'][idx] / 1000.0])
        marker_ins.set_data([traj_ins['E'][idx] / 1000.0], [traj_ins['N'][idx] / 1000.0])
        marker_ekf.set_data([traj_ekf['E'][idx] / 1000.0], [traj_ekf['N'][idx] / 1000.0])
        
        # Temps
        text_temps.set_text(f'Temps: {verite["t"][idx]:.1f} s ({verite["t"][idx]/60.0:.1f} min)')
        
        return line_verite, line_ins, line_ekf, marker_verite, marker_ins, marker_ekf, text_temps
    
    # Creation animation
    n_frames = int(np.ceil(len(verite['t']) / vitesse_lecture))
    print(f'[INFO] Animation: {n_frames} frames pour {len(verite["t"])} echantillons (vitesse x{vitesse_lecture})')
    anim = FuncAnimation(fig, animate, init_func=init, frames=n_frames,
                        interval=50, blit=True, repeat=True)
    
    return anim
