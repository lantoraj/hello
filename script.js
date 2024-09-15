// Wait for the DOM to load before initializing the map
document.addEventListener('DOMContentLoaded', () => {

    // Initialize the map and set its view to the Czech Republic
    const map = L.map('map').setView([49.8175, 15.4730], 7); // Coordinates of the Czech Republic

    // Add OpenStreetMap tiles to the map
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // List of towns with latitude, longitude, and population (example data)
    const towns = [
        { name: "Prague", lat: 50.0755, lon: 14.4378, population: 1300000 },
        { name: "Brno", lat: 49.1951, lon: 16.6068, population: 377407 },
        { name: "Ostrava", lat: 49.8209, lon: 18.2625, population: 289128 },
        { name: "Plzeň", lat: 49.7384, lon: 13.3736, population: 170936 },
        { name: "Liberec", lat: 50.7707, lon: 15.0582, population: 104445 },
        { name: "Olomouc", lat: 49.5955, lon: 17.2518, population: 100043 },
        { name: "SmallTown", lat: 50.0000, lon: 15.0000, population: 1500 } // Example of a small town under 2000 people
    ];

    // Function to simulate fetching hotel data from an API for a given town
    function fetchHotelDataForTown(townName) {
        // Simulated hotel data (in a real scenario, make an API call here)
        return new Promise((resolve) => {
            setTimeout(() => {
                // Simulating hotel data for the given town
                const hotels = [
                    { name: "Hotel A", stars: 4 },
                    { name: "Hotel B", stars: 3 }
                ];
                resolve(hotels);
            }, 1000); // Simulating API response delay
        });
    }

    // Filter towns with a population of more than 2000
    const filteredTowns = towns.filter(town => town.population > 2000);

    // Add markers for each filtered town to the map
    filteredTowns.forEach(town => {
        // Create a marker for each town
        const marker = L.marker([town.lat, town.lon])
            .addTo(map)
            .bindPopup(`<b>${town.name}</b><br>Hotels: <span id="hotels-${town.name}">Loading...</span>`);

        // Fetch hotel data for the town and update the popup
        fetchHotelDataForTown(town.name).then(hotels => {
            const hotelList = hotels.map(hotel => `${hotel.name} (${hotel.stars}★)`).join(', ');
            document.getElementById(`hotels-${town.name}`).innerText = hotelList;
        });
    });

});
