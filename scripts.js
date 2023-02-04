MAPS_API_KEY = 'AIzaSyCg3o9CaqqdhgfsGmPw2AGhypgFMJfbW4w'


function initMap() {
    const bristol = {
        lat: 51.454,
        lng: -2.587,
    }

    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 8,
        center: bristol,
    })



}

window.initMap = initMap;








async function ping() {
    let response = await fetch (
        'https://www.strava.com/api/v3/athlete/activities?before=1675109592&after=56&page=1&per_page=15',
        {
            headers: {
                authorization: 'Bearer c4363870176b91b610bcdab6c597f8b8ce59be24'
            }
        }
    )
    if (response.ok) {
        let json = await response.json()
    }  
}
