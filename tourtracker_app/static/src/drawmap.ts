export {}
let map: google.maps.Map;

function initMap(): void {
    map = new google.maps.Map(document.getElementById("map") as HTMLElement, {
        center: {lat: 0, lng: 0},
        zoom: 8,
        mapTypeId: 'terrain',
    })

    refreshMapData()

}

declare global {
    interface Window {
        initMap: () => void;
    }
}

window.initMap = initMap;

async function refreshMapData(): Promise<void> {
    const fetch_url_origin = window.location.origin;
    const fetch_url_pathname_components = window.location.pathname.split('/');
    const fetch_url_pathname = fetch_url_pathname_components[fetch_url_pathname_components.length - 1];
    const fetch_url = fetch_url_origin + '/tour/data/' + fetch_url_pathname;

    let response = await fetch (fetch_url, {
        method: 'GET',
    })

    if (response.ok) {
        let result = await response.json();
        result.forEach(element => {
            drawMap(element)
        })
        const finalActivity = result[result.length - 1];
        const finalLatLong = finalActivity.points[finalActivity.points.length - 1];
        map.panTo(finalLatLong);
    }
}

function drawMap(element): void {
    const hue = Math.floor(Math.random()*360);
    const saturation = 100;
    const value = 100;

    let path = new google.maps.Polyline({
        path: element.points,
        strokeColor: '#' + HSVToHex(hue, saturation, value),
        strokeOpacity: 1.0,
        strokeWeight: 2,
        clickable: true,
    });

    let border = new google.maps.Polyline({
        path: path.getPath(),
        strokeColor: '#ffffff',
        strokeOpacity: 1,
        strokeWeight: 4,
        zIndex: -1,
        visible: false,
    })

    let infoWindow = new google.maps.InfoWindow;
    google.maps.event.addListener(path, 'click', function(e) {
        let activity_date = new Date(element.activity_date)
        // checkForActiveInfoWindow(infoWindow)
        infoWindow.setPosition(e.latLng);
        infoWindow.setContent("<p>" + element.activity_name + "</p>" +
                              "<p>" + activity_date.getDate() + "/" + (activity_date.getMonth() + 1) + "/" + activity_date.getFullYear() + "</p>" +
                              `<p><a href="https://www.strava.com/activities/${element.strava_activity_id}">View on Strava</a></p>`)
        infoWindow.open(map)
        showActivePolylineBorder(border)
    })

    google.maps.event.addListener(infoWindow, 'closeclick', function(e) {
        hideActivePolylineBorder(border)
    })

    border.setMap(map)
    path.setMap(map)
}

function showActivePolylineBorder(borderPolyline): void {
    borderPolyline.setVisible(true)
}

function hideActivePolylineBorder(borderPolyline): void {
    borderPolyline.setVisible(false)
}

function HSVToHex(h: number,s: number,v: number): string {
    //https://www.rapidtables.com/convert/color/hsv-to-rgb.html
    //https://css-tricks.com/converting-color-spaces-in-javascript/
    // Convert saturation and value to decimal
    s /= 100;
    v /= 100;

    const chroma = s * v;
    const x = chroma * (1 - Math.abs((h/60) % 2 -1));
    const m = v - chroma;
    let rdash, gdash, bdash

    if (0 <= h && h < 60) {
        rdash = chroma; gdash = x; bdash = 0;
    } else if (60 <= h && h < 120) {
        rdash = x; gdash = chroma; bdash =0;
    } else if (120 <=h && h < 180) {
        rdash = 0; gdash = chroma; bdash = x;
    } else if (180 <= h && h <240) {
        rdash = 0; gdash = x; bdash = chroma;
    } else if (240 <= h && h < 300) {
        rdash = x; gdash = 0; bdash = chroma;
    } else if (300 <= h && h < 360) {
        rdash = chroma; gdash = 0; bdash = x;
    }

    let rgb = [
        Math.round((rdash + m) * 255),
        Math.round((gdash + m) * 255),
        Math.round((bdash + m) * 255),
    ];

    let hex = rgb.map((element) => {
        let tmp = element.toString(16);
        if (tmp.length < 2) {
            tmp = '0' + tmp
        }
        return tmp
    })

    return hex.join('')   
}

