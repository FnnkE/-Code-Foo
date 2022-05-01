var counter = 0;

function dataCallback(data, autoplay) {
    for (var i = 0; i < 6; i++) {
        if (i==0) {
            var video = document.getElementById("video")

            video.setAttribute('src', data.data[i].assets[(data.data[i].assets.length)-1].url);
            video.setAttribute('type', 'video/mp4')
            video.setAttribute('autoplay', autoplay)


            document.getElementById("title").innerHTML = data.data[i].metadata.title

           document.getElementById("description").innerHTML = data.data[i].metadata.description
        }
        else {

            var card = document.getElementById('card'+i)
            var title = document.getElementById('card-title'+i);
            var image = document.getElementById('card-image'+i)

            title.innerHTML = data.data[i].metadata.title;

            image.src = data.data[i].thumbnails[1].url
        }
    }
}

function callData(startIndex) {
    counter+=startIndex
    var script = document.createElement('script');
    script.src ="http://ign-apis.herokuapp.com/videos?startIndex=" + counter + "&count=6&callback=dataCallback"
    document.getElementsByTagName('head')[0].appendChild(script);
}

