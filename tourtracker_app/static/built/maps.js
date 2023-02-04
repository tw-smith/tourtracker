var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
let map;
// document.getElementById("draw").addEventListener('click', ()  => draw())
function postDatePicker() {
    return __awaiter(this, void 0, void 0, function* () {
        const form = document.getElementById("datePickerForm");
        const payload = {
            startDate: form.elements['startDate'].value,
            endDate: form.elements['endDate'].value
        };
        console.log(payload);
        let response = yield fetch('http://127.0.0.1:5000/get_activities', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            let result = yield response.json();
            console.log(result);
            result.forEach(element => {
                drawMap(element.points);
            });
        }
    });
}
function HSVToHex(h, s, v) {
    //https://www.rapidtables.com/convert/color/hsv-to-rgb.html
    //https://css-tricks.com/converting-color-spaces-in-javascript/
    // Convert saturation and value to decimal
    s /= 100;
    v /= 100;
    const chroma = s * v;
    const x = chroma * (1 - Math.abs((h / 60) % 2 - 1));
    const m = v - chroma;
    let rdash, gdash, bdash;
    if (0 <= h && h < 60) {
        rdash = chroma;
        gdash = x;
        bdash = 0;
    }
    else if (60 <= h && h < 120) {
        rdash = x;
        gdash = chroma;
        bdash = 0;
    }
    else if (120 <= h && h < 180) {
        rdash = 0;
        gdash = chroma;
        bdash = x;
    }
    else if (180 <= h && h < 240) {
        rdash = 0;
        gdash = x;
        bdash = chroma;
    }
    else if (240 <= h && h < 300) {
        rdash = x;
        gdash = 0;
        bdash = chroma;
    }
    else if (300 <= h && h < 360) {
        rdash = chroma;
        gdash = 0;
        bdash = x;
    }
    let rgb = [
        Math.round((rdash + m) * 255),
        Math.round((gdash + m) * 255),
        Math.round((bdash + m) * 255),
    ];
    let hex = rgb.map((element) => {
        let tmp = element.toString(16);
        if (tmp.length < 2) {
            tmp = '0' + tmp;
        }
        return tmp;
    });
    return hex.join('');
}
function drawMap(points) {
    const hue = Math.floor(Math.random() * 360);
    const saturation = 100;
    const value = 100;
    const path = new google.maps.Polyline({
        path: points,
        strokeColor: '#' + HSVToHex(hue, saturation, value),
        strokeOpacity: 1.0,
        strokeWeight: 2,
    });
    console.log(path);
    console.log('#' + HSVToHex(hue, saturation, value));
    path.setMap(map);
}
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("datePickerForm")) {
        const datePickerForm = document.getElementById("datePickerForm");
        const startDatePicker = document.createElement("input");
        startDatePicker.type = "date";
        startDatePicker.id = "startDate";
        startDatePicker.name = "startDate";
        const endDatePicker = document.createElement("input");
        endDatePicker.type = "date";
        endDatePicker.id = "endDate";
        endDatePicker.name = "endDate";
        const submitButton = document.createElement("button");
        submitButton.innerText = "Submit";
        datePickerForm.appendChild(startDatePicker);
        datePickerForm.appendChild(endDatePicker);
        datePickerForm.after(submitButton);
        submitButton.addEventListener("click", postDatePicker);
    }
});
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 51.454, lng: -2.857 },
        zoom: 8,
    });
}
window.initMap = initMap;
export {};
