var container = document.querySelector(".container");
var videoC = document.querySelector(".c-video");
var controls = document.querySelector(".controls");

var pl = document.getElementById("playlist");

var video = document.getElementById('video');

var prog = document.querySelector('.progress');

var playBTN = document.getElementById('play');

var loopBTN = document.getElementById('loop');
var loopActive = false;

var volumeBTN = document.getElementById('volume');
var muted = false;
var volumeSlider = document.getElementById('vol-control');
volumeSlider.value = 100;
var storedVol = 0;

var fsBTN = document.getElementById('fullscreen')
var fsActive = false;

var bar = document.querySelector(".progress-bar");

function togglePlayPause() {
    if (video.paused) {
        playBTN.className = 'pause';
        video.play();
    }
    else {
        playBTN.className = 'play';
        video.pause();
    }
}

function barProgess() {
    var progressPos = video.currentTime / video.duration;
    prog.style.width = progressPos * 100 + "%";
    if (video.ended) {
        callData(1)
    }
}

function videoSkip(c) {
    video.currentTime = (c.offsetX / bar.offsetWidth) * video.duration
}

playBTN.onclick = function () {
    togglePlayPause();
};

loopBTN.onclick = function () {
    if (loopActive) {
        video.loop = false;
        loopBTN.className = "nonactive";
        loopActive = false;
    }
    else {
        video.loop = true;
        loopBTN.className = "active";
        loopActive = true;
    }
};

volumeBTN.onclick = function () {
    if (muted) {
        video.muted = false;
        volumeBTN.className = "on";
        muted = false;
        video.volume = storedVol;
        volumeSlider.value = storedVol*100;
    }
    else {
        storedVol = video.volume;
        volumeSlider.value = 0;
        video.muted = true;
        volumeBTN.className = "muted";
        muted = true;
    }
};

function setVolume(val) {
    video.volume = val/100;
}


fsBTN.onclick = function () {
    if (fsActive) {
        fsActive = false
        document.exitFullscreen();
        fsBTN.className = "nonactive";
    }
    else {
        fsActive=true;
        videoC.requestFullscreen();
        fsBTN.className = "active";
    }

}

video.onclick = function () {
    togglePlayPause();
};

function nextVideo () {

}

bar.addEventListener("click", videoSkip, false);

video.addEventListener('timeupdate', barProgess, false);

video.addEventListener("mousemove", e => {
    const timer = video.getAttribute("timer");
    if (timer) {
        clearTimeout(timer);
        video.setAttribute("timer", "");
    }
    const t = setTimeout(() => {
        video.setAttribute("timer", "");
        video.classList.add("hide-cursor");
        video.style.opacity = 1;
        controls.style.transform = 'translateY(100%) translateY(-5px)';
    }, 3500);
    video.setAttribute("timer", t);
    video.classList.remove("hide-cursor");
    video.style.opacity = .75;
    controls.style.transform = "translateY(0)"
});

videoC.addEventListener("mouseleave", e => {
    video.style.opacity = 1;
    controls.style.transform = 'translateY(100%) translateY(-5px)';
})
