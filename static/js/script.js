setInterval(function(){

let playerId = window.location.pathname.split("/")[2]

fetch("/highest/"+playerId)

.then(res=>res.json())

.then(data=>{

document.getElementById("highestBid").innerText = data.bid

})

},2000)