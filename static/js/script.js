console.log("stuff")



console.log(1)


function readCSVFile(){
    var files = document.querySelector('#upload_csv').files;
    console.log(files)

    if(files.length > 0 ){

         // Selected file
         var file = files[0];

         // FileReader Object
         var reader = new FileReader();

         // Read file as string 
         reader.readAsText(file);

         // Load event
         reader.onload = function(event) {

              // Read file data
              var csvdata = event.target.result;

            
              //var rowData = csvdata.split('\n');
              
              $.post( "/get_csv_data",{
              csv_data: csvdata 
              });

              
         };

    }else{
         alert("Please select a file.");
    }

}
