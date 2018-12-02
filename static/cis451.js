$(document).ready(function(){
    $('button#salaryByDept').click(function(){
        $.ajax({
            url: '/Salaries/Department',
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                total_salaries_json = data['total_salary']
                departments_json = data['dname']
                total_salaries = []
                departments = []
                for (dept in departments_json){
                    departments.push(departments_json[dept]);
                    total_salaries.push(total_salaries_json[dept]);
                }
                
                
                departmentPlotData = [
                    {
                        x: departments,
                        y: total_salaries,
                        type: 'bar'
                    }
                ];

                Plotly.newPlot('departmentSalariesModalContent', departmentPlotData);
            }
        });
    });
    $('button#salaryByIndiv').click(function(){
        $.ajax({
            url: '/Salaries/Individual',
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                individual_salaries_json = data['salary']
                names_json = data['full_name']
                individual_salaries = []
                names = []
                for (person in names_json){
                    names.push(names_json[person]);
                    individual_salaries.push(individual_salaries_json[person]);
                }
                
                
                individualPlotData = [
                    {
                        x: names,
                        y: individual_salaries,
                        type: 'bar'
                    }
                ];

                Plotly.newPlot('individualSalariesModalContent', individualPlotData);
            }
        });
    });
    $(document).on('change', 'input.orderEntryQuantity', function(){
        var itemPrice = $(this).parent().parent().find('input.orderEntryItem').val();
        if (itemPrice != ''){
            var priceCapture = /\(([^)]+)\)/;
            var unitPrice = parseFloat(priceCapture.exec(itemPrice)[1].replace('$',''));
            var total = '$'+(parseInt($(this).val()) * unitPrice).toFixed(2);
            $(this).parent().parent().find('input.orderEntryTotalPrice').val(total);
        }
    });
    $(document).on('change', 'input.orderEntryItem', function(){
        var itemQuantity = $(this).parent().parent().find('input.orderEntryQuantity').val();
        if (itemQuantity != ''){
            var priceCapture = /\(([^)]+)\)/;
            var unitPrice = parseFloat(priceCapture.exec($(this).val())[1].replace('$',''));
            var total = '$'+(parseInt(itemQuantity) * unitPrice).toFixed(2);
            $(this).parent().parent().find('input.orderEntryTotalPrice').val(total);
        }
    });
    $('button.companiesByRegionBtn').click(function(){
        var region = $(this).attr("name");
        $('h5#companiesByRegionModalLabel').html(region+" Region");

        $.ajax({
            url: '/Sales-Regions/Companies/'+region,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                names_json = data['name']
                total_ordered_json = data['total_ordered']
                names = []
                total_ordered = []
                for (company in names_json){
                    names.push(names_json[company]);
                    total_ordered.push(total_ordered_json[company]);
                }
                
                
                regionSalesPlotData = [
                    {
                        x: names,
                        y: total_ordered,
                        type: 'bar'
                    }
                ];

                Plotly.newPlot('companiesByRegionModalContent', regionSalesPlotData);
            }
        });
    });
    $('#salesEmployeeSelectionBox').change(function(){
        let essn = $(this).val();
        $.ajax({
            url: '/Sales-Employees/'+essn,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                var employeeInfo = JSON.parse(data['employeeInfo']);
                var totalOrdered = employeeInfo['total_ordered'][0].toLocaleString();
                var totalPrice = employeeInfo['total_price'][0].toLocaleString(undefined, {maximumFractionDigits:2, minimumFractionDigits:2});
                var name = data['employeeName'];
                var clientInfo = JSON.parse(data['clientInfo']);
                $('tbody#clientInformation').html("");
                $('h3#employeeName').html("Displaying information for <b>"+name+"</b>");
                $('h5#employeeTotalSales').html(name+" has sold <b>"+totalOrdered+" total items</b> and has generated <b>$"+totalPrice+" in total sales");
                $('div#employeeSummaryInformation').css("display", "block");
    
                for (client in clientInfo['name']){
                    $('tbody#clientInformation').append('<tr><td scope="col-8">'+clientInfo['name'][client]+'</td><td scope="col-2">'+clientInfo['total_ordered'][client]+'</td><td scope="col-2">$'+clientInfo['total_price'][client].toLocaleString(undefined, {maximumFractionDigits:2, minimumFractionDigits:2})+'</td></tr>')
                }
            }
        });
    });
});