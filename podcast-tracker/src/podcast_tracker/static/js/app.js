// API Base URL
const API_BASE = '';

// State
let currentPage = 1;
let currentPodcastFilter = '';
let podcasts = [];

// DOM Elements
const episodesList = document.getElementById('episodesList');
const loading = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');
const refreshBtn = document.getElementById('refreshBtn');
const podcastFilter = document.getElementById('podcastFilter');
const pagination = document.getElementById('pagination');
const totalPodcastsEl = document.getElementById('totalPodcasts');
const totalEpisodesEl = document.getElementById('totalEpisodes');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPodcasts();
    loadEpisodes();
    
    // Event listeners
    refreshBtn.addEventListener('click', handleRefresh);
    podcastFilter.addEventListener('change', handleFilterChange);
    
    // Auto-refresh every 5 minutes
    setInterval(loadEpisodes, 5 * 60 * 1000);
});

// Load podcasts for filter
async function loadPodcasts() {
    try {
        const response = await fetch(`${API_BASE}/api/podcasts`);
        podcasts = await response.json();
        
        totalPodcastsEl.textContent = podcasts.length;
        
        // Populate filter
        podcastFilter.innerHTML = '<option value="">Todos los podcasts</option>';
        podcasts.forEach(podcast => {
            const option = document.createElement('option');
            option.value = podcast.id;
            option.textContent = podcast.name;
            podcastFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading podcasts:', error);
    }
}

// Load episodes
async function loadEpisodes(page = 1) {
    showLoading();
    
    try {
        let url = `${API_BASE}/api/episodes?page=${page}&page_size=20`;
        if (currentPodcastFilter) {
            url += `&podcast_id=${currentPodcastFilter}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        totalEpisodesEl.textContent = data.total;
        
        if (data.episodes.length === 0) {
            showEmptyState();
        } else {
            displayEpisodes(data.episodes);
            displayPagination(data);
        }
    } catch (error) {
        console.error('Error loading episodes:', error);
        hideLoading();
    }
}

// Display episodes
function displayEpisodes(episodes) {
    hideLoading();
    hideEmptyState();
    
    episodesList.innerHTML = '';
    
    episodes.forEach(episode => {
        const card = createEpisodeCard(episode);
        episodesList.appendChild(card);
    });
}

// Create episode card
function createEpisodeCard(episode) {
    const card = document.createElement('div');
    card.className = 'episode-card';
    
    const podcastName = episode.podcast ? episode.podcast.name : 'Unknown Podcast';
    const formattedDate = formatDate(episode.pub_date);
    
    card.innerHTML = `
        <div class="episode-header">
            <div class="episode-info">
                <div class="episode-podcast">${podcastName}</div>
                <h3 class="episode-title">${escapeHtml(episode.title)}</h3>
                <div class="episode-meta">
                    <span>📅 ${formattedDate}</span>
                    ${episode.duration ? `<span>⏱️ ${episode.duration}</span>` : ''}
                </div>
            </div>
        </div>
        ${episode.description ? `<p class="episode-description">${escapeHtml(episode.description)}</p>` : ''}
        <div class="episode-actions">
            ${episode.spotify_url ? 
                `<a href="${episode.spotify_url}" target="_blank" class="btn btn-primary">
                    🎧 Escuchar en Spotify
                </a>` : 
                `<a href="${episode.episode_url}" target="_blank" class="btn btn-primary">
                    🎧 Escuchar
                </a>`
            }
            <button class="btn btn-secondary" onclick="markAsListened(${episode.id})">
                ✓ Marcar como escuchado
            </button>
        </div>
    `;
    
    return card;
}

// Mark episode as listened
async function markAsListened(episodeId) {
    try {
        const response = await fetch(`${API_BASE}/api/episodes/${episodeId}/listened`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ listened: true })
        });
        
        if (response.ok) {
            // Reload episodes
            loadEpisodes(currentPage);
        }
    } catch (error) {
        console.error('Error marking episode as listened:', error);
    }
}

// Handle refresh
async function handleRefresh() {
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<span class="refresh-icon">🔄</span> Actualizando...';
    
    try {
        const response = await fetch(`${API_BASE}/api/podcasts/refresh`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        // Show notification
        alert(data.message);
        
        // Reload episodes
        await loadEpisodes(currentPage);
    } catch (error) {
        console.error('Error refreshing podcasts:', error);
        alert('Error al actualizar podcasts');
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<span class="refresh-icon">🔄</span> Actualizar';
    }
}

// Handle filter change
function handleFilterChange(e) {
    currentPodcastFilter = e.target.value;
    currentPage = 1;
    loadEpisodes(currentPage);
}

// Display pagination
function displayPagination(data) {
    pagination.innerHTML = '';
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '← Anterior';
    prevBtn.disabled = data.page === 1;
    prevBtn.onclick = () => {
        currentPage = data.page - 1;
        loadEpisodes(currentPage);
    };
    pagination.appendChild(prevBtn);
    
    // Page info
    const pageInfo = document.createElement('span');
    pageInfo.className = 'page-info';
    pageInfo.textContent = `Página ${data.page} de ${data.total_pages}`;
    pagination.appendChild(pageInfo);
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Siguiente →';
    nextBtn.disabled = data.page === data.total_pages;
    nextBtn.onclick = () => {
        currentPage = data.page + 1;
        loadEpisodes(currentPage);
    };
    pagination.appendChild(nextBtn);
}

// Utility functions
function showLoading() {
    loading.classList.remove('hidden');
    episodesList.classList.add('hidden');
    emptyState.classList.add('hidden');
    pagination.classList.add('hidden');
}

function hideLoading() {
    loading.classList.add('hidden');
    episodesList.classList.remove('hidden');
}

function showEmptyState() {
    loading.classList.add('hidden');
    episodesList.classList.add('hidden');
    emptyState.classList.remove('hidden');
    pagination.classList.add('hidden');
}

function hideEmptyState() {
    emptyState.classList.add('hidden');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        return 'Hoy';
    } else if (diffDays === 1) {
        return 'Ayer';
    } else if (diffDays < 7) {
        return `Hace ${diffDays} días`;
    } else {
        return date.toLocaleDateString('es-ES', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
