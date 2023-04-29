//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises
//https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch

var foodMenu = fetchJSON("./burgers.json");
var globFries = false;
var globUpsize = false;

async function fetchJSON(requestURL){
    const response = await fetch(requestURL);
    const json = await response.json();
    return json;
}

function listMenu(json){
    json
        .then( jsonData => _listMenu(jsonData))
        .catch((error) => console.error("Error:", error))

    function _listMenu(json){
        var ul = document.getElementById("burger_list");
        for(i=0; i<json.burgers.length; i++){
            let li = document.createElement("li");
            li.appendChild(document.createTextNode(json.burgers[i].name));
            li.setAttribute("id","burger"+i);
            li.setAttribute("onclick", "showBurgerInfo("+i+")");
            ul.appendChild(li);
        }
        return json;
    }
    return json;
}

function showBurgerInfo(burgerIndex){
    foodMenu
        .then( (json) => _showBurgerInfo(json,burgerIndex) )
        .catch((error) => console.error("Error:", error))
    
    function _showBurgerInfo(json,burgerIndex){
        let target = document.getElementById("burger_id");
        target.innerHTML = burgerIndex;

        target = document.getElementById("burger_selected");
        target.innerHTML = "Selected: " + json.burgers[burgerIndex].name;

        target = document.getElementById("price");
        target.innerHTML = "$ "+ json.burgers[burgerIndex].price;

        target = document.getElementById("layers");
        target.innerHTML = "";
        for(i=0; i<json.burgers[burgerIndex].layers.length; i++){
            let li = document.createElement("li");
            li.appendChild(document.createTextNode(json.burgers[burgerIndex].layers[i]));
            li.setAttribute("id","layer"+i);
            target.appendChild(li);
        }

        target = document.getElementById("burger_img");
        target.innerHTML = "";
        let elem = document.createElement("img");
        elem.src = json.burgers[burgerIndex].imgsrc;
        elem.width = 640;
        target.appendChild(elem);
        return json;
    }
    return;
}

function pageLoad(){
    listMenu(foodMenu)
        .catch((error) => console.error("Error:", error))
    
}

function buttonFries(){
    let target = document.getElementById("button_fries");
    if(globFries){
        globFries = false;
        target.style.background="#D0D0D0";
    }else{
        globFries=true;
        target.style.background="#B0EEB0";
    }
}
function buttonUpsize(){
    let target = document.getElementById("button_upsize");
    if(globUpsize){
        globUpsize = false;
        target.style.background="#D0D0D0";
    }else{
        globUpsize=true;
        target.style.background="#B0EEB0";
    }
}

function buttonAsk(){
    foodMenu
        .then( (json) => _promptItem(json) )
        .catch((error) => console.error("Error:", error))

    function _promptItem(json){
        let target = document.getElementById("burger_id");
        let burgerID = Number(target.innerHTML);
        let price = json.burgers[burgerID].price;
        let outStr = "";
        if(burgerID < 0){return}
        if(!confirm("Would you like to order a " + json.burgers[burgerID].name + " ?")){return}
        outStr += "So that's 1 " + json.burgers[burgerID].name;
        if(globFries){
            price += 2.00;
            outStr += " with fries"
        }else{
            outStr += ", no fries"
        }

        if(globUpsize){
            price += 1.50;
            outStr += ", upsized to a large meal. "
        }else{
            outStr += ", just a regular meal. "
        }

        outStr += "The total price of the meal is: $" + price + "." 

        target = document.getElementById("what_u_ordered");
        target.innerHTML = outStr;
    }
    return;
}
