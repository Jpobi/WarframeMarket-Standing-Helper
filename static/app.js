
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/service-worker.js')
        .then(function(registration) {
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }, function(error) {
            console.log('ServiceWorker registration failed: ', error);
        });
}



document.addEventListener('DOMContentLoaded', function() {
    var factionSelect = document.getElementById('factions');
    var orderSelect = document.getElementById('orderType');
    factionSelect.addEventListener('change', updateTable);
    orderSelect.addEventListener('change', updateTable);
});
function updateDatabase() {
    var btn=document.getElementById("fetch-button");
    var oldtext=btn.textContent;
    btn.textContent="Updating...";
    btn.disabled = true;
    fetch('/updateMods')
        .then(response => {
            if (!response.ok) {
                btn.textContent="Try fetching again";
                btn.disabled = false;
                throw new Error('Error Updating database: '+ response.statusText);
            }
            return response.text();
        })
        .then(text => {
            console.log('Database update successful:', text);
            btn.textContent=oldtext;
            btn.disabled = false;
            alert("Database updated successfully");
        })
        .catch(error => {
            console.error('Error updating database:', error);
            btn.textContent=oldtext;
            btn.disabled = false;
            alert("Error updating database. Check console for details.");
        });
}
var socket = io();

var btn=document.getElementById("fetch-button");
var oldtext=btn.textContent;
function startTask() {
    btn.textContent="Updating...";
    btn.disabled = true;
    socket.emit('start_task');
}

//TODO: Add progress bar
//TODO: Mandar Current/total mods
socket.on('task_progress', function(progress) {
    console.log("progress: ",progress);
    if (progress == 100) {
        btn.textContent=oldtext;
        btn.disabled = false;
        }
        document.getElementById('progress').innerText = 'Progress: ' + progress.toString() + '%';
        });
        
//TODO: Add error handling
//socket onerror -> print error
function updateTable() {
    var factionSelect = document.getElementById('factions');
    var orderSelect = document.getElementById('orderType');
    var modsContainer = document.getElementById('cards-container');
    var selectedFactionId = factionSelect.value;
    var selectedOrderType = orderSelect.value;

    // Fetch updated mods based on selected faction
    fetch(`/mods/${selectedFactionId}/${selectedOrderType}`)
        .then(response => response.json())
        .then(mods => {
            // Clear existing mods
            modsContainer.innerHTML = '';

            // Add new mods to container
            mods.forEach(mod => {
                const card = createModCard(mod,selectedOrderType);
                modsContainer.appendChild(card);
            });
        })
        .catch(error => {console.log(response);console.error('Error fetching mods:', error)});
}

function createModCard(mod,orderType="") {
    const card = document.createElement('div');
    card.classList.add('card');
    card.setAttribute('factionId', mod.factionId);
    card.dataset.faction = mod.factionId;
    factionLogoSrc=`/static/faction_logos/${mod.factionId}.png`;

    if(orderType=="price"){
        highlightedSection=`<p class="highlighted"><strong>Online Avg Offer Price:</strong> ${mod.offerPrice} pl</p>
                <p><strong>Most Repeated Price:</strong> ${mod.mostRepeatedOffer} pl</p>
                <p><strong>Amount Sold 48Hs:</strong> ${mod.amount48} units</p>`;
    } else{
        highlightedSection=`<p><strong>Online Avg Offer Price:</strong> ${mod.offerPrice} pl</p>
                <p><strong>Most Repeated Price:</strong> ${mod.mostRepeatedOffer} pl</p>
                <p class="highlighted"><strong>Amount Sold 48Hs:</strong> ${mod.amount48} units</p>`;
    }
    card.innerHTML = `
        <h2>${mod.name}</h2>
        <div class="card-content">
            <p><strong>Max Average Sold:</strong> ${mod.MaxAvgSold} pl</p>
            ${highlightedSection}
            <p><strong>Amount Sold 90days:</strong> ${mod.amount90} units</p>
            <p><strong>Factions:</strong> ${mod.factionNames}</p>
            <p><strong>URL:</strong> <a href="https://warframe.market/items/${mod.url_name}" target="_blank">warframe.market</a></p>
            <img class="faction_logo" src="${factionLogoSrc}" alt="Faction Logo">
        </div>
    `;

    return card;
}