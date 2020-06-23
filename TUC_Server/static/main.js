window.onload = loadMap;

var _id;
var _map;
var vector;
var count = 0;
var c_total = 0;

function loadMap(){
    loadLocation();
    loadGeo();
    loadPointsLoop();
    window.setInterval(loadPointsLoop,5000);
}

function loadLocation(){
    var container = document.getElementById('popup');
    var content = document.getElementById('popup-content');
    var overlay = new ol.Overlay({
        element: container,
        //autoPan: true,
        autoPanAnimation: {
          duration: 250
        }
    });
    // mapa 1
    _map = new ol.Map({
        view: new ol.View({
            center: [-964768.9865389101, 4953525.578932142],
            zoom: 16,
            maxZoom: 50,
        }),
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            })
        ],
        target: 'js-map',
        overlays: [overlay],    
    })

    // _map = map;
    _map.on('click', function(e){
        console.log(e.coordinate);
    })

    _map.addControl(new ol.control.FullScreen());

    // vector layers   
    _map.on('click', function(e){
        _map.forEachFeatureAtPixel(e.pixel, function(feature, layer){
            console.log(feature);
        })
    })

    var feature_onHover;
    _map.on('pointermove', function(evt) {
        feature_onHover = _map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
            return feature;
            });
        if (feature_onHover) {
            overlay.setPosition(evt.coordinate);
            content.innerHTML = "<b>ID: </b>" + feature_onHover.getProperties().name + "<br>" + "<b>Battery: </b>" + feature_onHover.getProperties().battery;
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    });
    loadPointsLoop();
}

function loadPointsLoop()
{
    var stylePoints = function(feature){

        var color;
        // console.log(feature.get("name"));
        if(feature.get("status")=="0"){
            color = "#3ECC39";
        }
        else {
            color = "#E51B14";
        }

        var circStyle = new ol.style.Style({
            image: new ol.style.Circle({
                color: color,
                radius:8,
                fill: new ol.style.Fill({
                    color: color,
                })
            })
        });
        return circStyle;
    };

    
    var newSource = new ol.source.Vector({
        format: new ol.format.GeoJSON(),
        url: 'map1.geojson'
    })

    var _tucs = new ol.layer.Vector({
        source: newSource,
        visible: true,
        style: stylePoints
    });

    _map.addLayer(_tucs);
    newSource.once('change',function
    ()
    {
        if(vector)
        {
            _map.removeLayer(vector);
        }
        vector = _tucs
    })
}

function loadGeo(){
    //mapa 2 - geofencing

    var raster = new ol.layer.Tile({
        source: new ol.source.OSM()
    });

    var source = new ol.source.Vector({
        url: 'geomapping.geojson',
        format: new ol.format.GeoJSON()
    });
    var vector = new ol.layer.Vector({
        source: source,
        style: new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(244, 164, 96, 0.2)'
            }),
            stroke: new ol.style.Stroke({
                color: '#ffcc33',
                width: 2
            }),
            image: new ol.style.Circle({
                radius: 7,
                fill: new ol.style.Fill({
                    color: '#ffcc33'
                })
            })
        })
    });

    // cria o mapa para o geofencing
    const map2 = new ol.Map({
        view: new ol.View({
            center: [-964768.9865389101, 4953525.578932142],
            zoom: 14,
            maxZoom: 50,
        }),
        layers: [raster, vector],
        target: 'js-map2'      
    })
    

    var draw, snap;

    function addDraw(){
        if(draw != null)
        {
            draw.on('drawend', drawEnd);
        }
        draw = new ol.interaction.Draw({
            name: "geofencing",
            source: source,
            type: "Polygon"
        });
        
        map2.addInteraction(draw);
        draw.on('drawstart', function(e) {
             map2.getLayers().getArray()[1].getSource().clear();
        });
        snap = new ol.interaction.Snap({source: source});
        map2.addInteraction(snap);
        
    }
    function drawEnd(){
        map2.removeInteraction(draw);
    }

    $(document).ready(function(){
        $("#modifyDraw").on('click', function(){
            var modify = new ol.interaction.Modify({
                source: source
            });
            map2.addInteraction(modify);
        });
    });
    
    addDraw();

    $(document).ready(function(){
        $("#deleteDraw").on('click', function(){
            // console.log("cliquei")
            confirm("You sure?");
            vector.getSource().clear();
        });
    });

    confirmGeo(source);
    
    // permite mapa em fullscreen
    map2.addControl(new ol.control.FullScreen());
}


function confirmGeo(source){
    $(document).ready(function(){

        source.on('addfeature', function(evt){
            count += 1
            c_total += 1;
            console.log("CONTADOR::::: "+ c_total);
            // console.log("SOOOOUUUUURRRCCEEEEE");
            // ao clicar em "Confirm", o gestor confirma o desenho do geofencing
            $("#confirmDraw").on('click', function(){
                console.log("COUNT A SERIO: ",count);
                if(count > 1)
                {
                    count -= 1;
                    return;
                }
                else
                {
                    count = c_total;
                }
                
                // console.log("CLIIIIICKKKK");
                var feature = evt.feature;
                var coords = feature.getGeometry().getCoordinates();
                var coords_send = [];
                for (var i = 0; i < coords[0].length-1; i++){
                    var str_points = "";
                    // console.log(coords[0][i][0]);
                    for(var j = 0; j < 2; j++)
                    {   
                        coords_temp = ol.proj.transform(coords[0][i], 'EPSG:3857', 'EPSG:4326');
                        // console.log("Bom dia");
                        if(j == 0)
                        {
                            str_points += coords_temp[j] + ",";  
                        }
                        else
                        {
                            str_points += coords_temp[j]; 
                        }                      
                    }
                    // console.log(str_points);
                    coords_send[i] = str_points;
                }
                // console.log("novo geof");
                // console.log(coords_send);
                var sendData = {
                    coordinates: coords_send,
                } 
                alert("you sure?");
                $.ajax({
                    type:'POST',
                    data: sendData,
                    url:'/geoFencing'
                });
            });
    
        });
    });
}


function deleteRow(btn) {
    var row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

// adicionar users à tabela
$(document).ready(function(){
    $("#add").on('click', function(){

        var table = document.getElementById("#tableUsers");
        var totalRows = $("#tableUsers").find('tr').length;
        var rowDelete = totalRows + 1;

        $("#tableUsers tr:last").after('<tr id="row_'+rowDelete+'"><td>'+$('#idUser').val()+'</td><td>'+$('#name').val()+'</td><td>'+$('#mail').val()+'</td><td><input type="submit" class="menos" id="del_'+rowDelete+'" value="DELETE"/></td></tr>');
        
        var sendData = {
            id: $('#idUser').val(),
            name: $('#name').val(),
            email: $('#mail').val(),
        }

        $.ajax({
            url:'/add_user',
            type:'POST',
            data: sendData,
            success: function(sendData) {
            }
        });
    });
});




// ao clicar numa entrada da tabela, dispor de toda a informação
$(document).ready(function($){
    $("#trot tr").click(function(){
        window.location = $(this).data("href");
        function getId(element){
            var id, idArr;
            // id = 'del_número'
            id = element.attr('id');
            // separa em dois o id: del_ + número
            idArr = id.split("_");
            // retorna o número (da row)
            return idArr[idArr.length-1];
        }
    
        var currentEle, rowNo;
        // obtém o id da row selecionada
        currentEle = $(this);
        // número da row selecionada
        rowNo1 = getId(currentEle);
        var id_card = document.getElementById("row_"+rowNo1).cells[0].innerHTML;
        // console.log("AGORA VAI")
        // console.log(id_card);
        localStorage.setItem("id",id_card);
       
    });
});

// ELIMINAR UMA ENTRADA DA TABELA

$(document).on('click', '.menos', function(){

    function getId(element){
        var id, idArr;
        // id = 'del_número'
        id = element.attr('id');
        // separa em dois o id: del_ + número
        idArr = id.split("_");
        // retorna o número (da row)
        return idArr[idArr.length-1];
    }

    var currentEle, rowNo;
    // obtém o id da row selecionada
    currentEle = $(this);
    // número da row selecionada
    rowNo = getId(currentEle);

    var id_del = document.getElementById("row_"+rowNo).cells[0].innerHTML;
    
    // console.log(id_del);
    // remove a row correspondente
    $("#row_"+rowNo).remove();
    var sendData = {
        id: id_del
    }
    $.ajax({
        url:'/delete_user',
        type:'POST',
        data: sendData,
        success: function(sendData) {
        }
    });

});
 
// TABELA DETAILS

(function updateDetails() {
    var _id = localStorage.getItem("id");
    var sendData;
    if(_id == null)
    {
        sendData = 
        {
            id: 1,
        }
    }
    else
    {
        sendData = 
        {
            id: _id,
        }
    }
    
    $.ajax({
        cache:false,
        url:"/get_useTime",
        type: "POST",
        data:sendData,
        success: function(data){
                var allRows = data.split(/\r?\n|\r/);
                var table;
                for(var singleRow=0; singleRow<allRows.length;singleRow++){
                    table += "<tr>";
            
                    var rowCells = allRows[singleRow].split(';');
                    for(var rowSingleCell=0; rowSingleCell<rowCells.length; rowSingleCell++){
                        table += "<td>";
                        table += rowCells[rowSingleCell];
        
                        table += "</td>";
                    }
            
                    table += "</tr>"
            
                }
                $("#tableDetails").html(table);
        }        
    }).then(function(){
        // console.log("reload details?");
        setTimeout(updateDetails, 1000);      
    });
})();

// TABELA DE TROTINETES
(function updateTrots() {
    $.ajax({
        url:"/scooter_list",
        dataType:"text",
        cache: false,
        success: function(data){
                var allRows = data.split(/\r?\n|\r/);
                var table;
                for(var singleRow=0; singleRow<allRows.length;singleRow++){
                    id_noT = singleRow;
                    table += "<tr class='upTrot' id='row_"+id_noT+"'>";

                    var rowCells = allRows[singleRow].split(';');
                    for(var rowSingleCell=0; rowSingleCell<rowCells.length; rowSingleCell++){
                        table += '<td id="del_'+id_noT+'">';
                        table += rowCells[rowSingleCell];
                        table += '</td>';
                    }

                    table += "</tr>";
                }
                $("#trot").html(table);
                $("td:contains('AVAILABLE')").addClass('avaBg');
                $("td:contains('IN USE')").addClass('useBg');
                $("#trot").on("click", "tr", function(e){
                    window.location.href = "details";
                });
        }
    }).then(function(){
        setTimeout(updateTrots, 7000);
    });
})();





(function updateUsers() {
    $.ajax({
        url:"/user_list",
        dataType:"text",
        cache: false,
        success: function(data){
            var allRows = data.split(/\r?\n|\r/);
            var table = "<table>";
            for(var singleRow=1; singleRow<allRows.length;singleRow++){
                id_no = singleRow;
                table += "<tr id='row_"+id_no+"'>";
        
                var rowCells = allRows[singleRow].split(';');
                for(var rowSingleCell=0; rowSingleCell<rowCells.length; rowSingleCell++){
                    if(singleRow == 0){
                        table += "<th id='delete_"+id_no+"'>";
                        table += rowCells[rowSingleCell];
                        table += "</th>";
                    } else{
                        table += "<td>";
                        table += rowCells[rowSingleCell];
        
                        if(rowSingleCell == rowCells.length - 1){
                            table += '<td><input type="submit" class="menos" id="del_'+id_no+'" value="DELETE"/></td>';
                            table += "</td>";
                        } else{
                            table += "</td>";
                        }
                    }
                }
        
                if(singleRow == 0){
                    table += "</tr>";
                } else {
                    table += "</tr>"
                }
            }
            // $("#tableUser2").append(table);
            $("#tableUsers").html(table);
        }
    }).then(function(){
        setTimeout(updateUsers, 8500);
    });
})();
/// LOGIN //////////


//
$(document).ready(function($){
    $("#login").click(function(){
            var sendData = {
                email: document.getElementById('email').value,
                pass: document.getElementById('pass').value,
            }
            $.ajax({
                url: "/check_credentials",
                type: "POST",
                data: sendData, 
                success: function(response) {
                    if(response == "false")
                    {
                        alert("Utilizador e/ou Password errados");
                    }
                    else
                    {
                        window.location = response;
                    }
                }
            }); 
    });
});

// $.ajax({
//     url:'/user_list',
//     dataType:"text",
// }).done(loadUsers)


