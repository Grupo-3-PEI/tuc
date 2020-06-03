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
        console.log("AGORA VAI")
        console.log(id_card);

        var sendDataT = {
            send_card: id_card,
        }

        $.ajax({
            url:'/more_info',
            type:'POST',
            data: send_card,
            success: function() {
            }
        });
    });
});

// TABELA DE DETALHES

function loadDetails(data){
    var allRows = data.split(/\r?\n|\r/);
    var table = "<table>";
    for(var singleRow=1; singleRow<allRows.length;singleRow++){
        table += "<tr>";

        var rowCells = allRows[singleRow].split(',');
        for(var rowSingleCell=0; rowSingleCell<rowCells.length; rowSingleCell++){
            if(singleRow == 0){
                table += "<th>";
                table += rowCells[rowSingleCell];
                table += "</th>";
            } else{
                table += "<td>";
                table += rowCells[rowSingleCell];

                if(rowSingleCell == rowCells.length - 1){
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
    $("#tableDetails").append(table);
}


$.ajax({
    url:"/get_useTime",
    dataType:"text",
}).done(loadDetails)


