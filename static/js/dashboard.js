$("#dashboardform").steps({
    bodyTag: "fieldset",
    labels: {finish: "Submit"},
    startIndex: 0,
    onInit: function (event, currentIndex, newIndex){
        console.log("oninit")
        console.log(currentIndex, newIndex)
        // save Button
        var saveA = $("<a>").attr("href","#").attr("id","saveBtn").text("Save");
        saveA.on('click', function(){
            alert("save")
            // save form data

        });
        var saveBtn = $("<li>").attr("aria-disabled",false).append(saveA);
        $(document).find(".actions ul").prepend(saveBtn);

        // summary Button
        var summaryA = $("<a>").attr("href","#").attr("data-toggle","modal").attr("data-target","#summaryInfo").attr("id","summaryBtn").text("Summary");
        var summaryBtn = $("<li>").attr("aria-disabled",false).append(summaryA);
        $(document).find(".actions ul").prepend(summaryBtn)

        summaryBtn.on ('click', function(){
            alert("summary")
            // display summary
        })


    },
    onStepChanging: function (event, currentIndex, newIndex){
        console.log("step changed")
        console.log(currentIndex, newIndex);
        return true;
    }
});

// --------------------------CASE PAGE 0 ----------------------------------------------
// ---- Add Child Row Table -------------------------------

function format2 ( d ) {
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
        '<tr>'+
            '<td style="font-weight:bold">Gender:</td>'+
            '<td>'+d[6]+'</td>'+
            '<td style="font-weight:bold">Age:</td>'+
            '<td>'+d[4]+'</td>'+
            '<td style="font-weight:bold">EGFR:</td>'+
            '<td>'+d[9]+'</td>'+
            '<td style="font-weight:bold">TP53:</td>'+
            '<td>'+d[10]+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td style="font-weight:bold">IDH1:</td>'+
            '<td>'+d[11]+'</td>'+
            '<td style="font-weight:bold">IDH2:</td>'+
            '<td >'+d[12]+'</td>'+
            '<td style="font-weight:bold">Tumor Grade:</td>'+
            '<td>'+d[13]+'</td>'+
            '<td style="font-weight:bold">Tumor Stage:</td>'+
            '<td >'+d[14]+'</td>'+
        '</tr>'+
    '</table>';
}


$('#caseSample').DataTable({
    "ajax": "/sample/api1",
    "lengthMenu": [[5, 25, 50, -1], [5, 25, 50, "All"]],
    "ordering" : false,
    "searching" : true,
//    "destroy" : true,
//    "autoWidth": false,
    "columnDefs": [
        {
            'targets': 0,
            'checkboxes': {
               'selectRow': true
            },
            'searchable': false,
            'orderable': false,
            'className': 'select-checkbox',
        },
        {
            "className":"details-control",
            "orderable":false,
            "data":null,
            "defaultContent": '',
            "width": "10px",
            targets : 1
        },
        {
            "targets": [ 4 ],
            "visible": false
        },
        {
            "targets": [ 6 ],
            "visible": false
        },
        {
            "targets": [ 9 ],
            "visible": false
        },
        {
            "targets": [ 10 ],
            "visible": false
        },{
            "targets": [ 11 ],
            "visible": false
        },
        {
            "targets": [ 12 ],
            "visible": false
        },
        {
            "targets": [ 13 ],
            "visible": false
        },
        {
            "targets": [ 14 ],
            "visible": false
        }
    ],
    "select": {
        "style": 'multi',
        "selector": 'td:first-child'
    },
    "order": [[1, 'asc']]
});


$('#caseSample tbody').on('click', 'input[type="checkbox"]', function(){
  // If checkbox is not checked
  if(!this.checked){
     var el = $('#caseSample-select-all').get(0);
     // If "Select all" control is checked and has 'indeterminate' property
     if(el && el.checked && ('indeterminate' in el)){
        // Set visual state of "Select all" control
        // as 'indeterminate'
        el.indeterminate = true;
     }
  }
});

$('#caseSample tbody').on('click', 'td.details-control', function () {
    var tr = $(this).closest('tr');
    var caseTable = $('#caseSample').DataTable();
    var row = caseTable.row( tr );

    if(row.child.isShown()) {
        // This row is already open - close it
        row.child.hide();
        tr.removeClass('shown');
    }else {
        // Open this row
        row.child( format2(row.data()) ).show();
        tr.addClass('shown');
    }
});


$(document).delegate(".casePlusAddFilter", "click", function (){
    if($("#case_disease_name").val().trim() == "" || $("#case_disease_name").val() == null){
        swal("Please select disease name")
    }
    else {
        if ($('#caseAddFilter').is(':empty')){
            var row_id = 0;
        }
        else{
            var row_id = this.id.split('_')[2];
        }
        this.disabled = true
        row_id = parseInt(row_id) + 1;

        $.ajax({
            url: "/features",
            type: "GET",
            dataType: "json",
            success: function (data) {
                var f_data = '<div id="crow_'+row_id+'" class="row m-n"><div class="form-group">'+
                    '<div class="col-lg-4 ui-widget" style="padding-left:5px;">'+
                        '<a href="#" id="caseplus_row_'+row_id+'" class="casePlusAddFilter m-l-xs m-r-xs m-t-xs" style="margin-top:5px !important;">'+
                            '<i class="fa fa-plus-square" aria-hidden="true"></i>'+
                        '</a>'+
                        '<a href="#" id="caseminus_row_'+row_id+'" class="caseMinusRemoveFilter m-l-xs m-r-xs m-t-xs" style="margin-top:5px !important;">'+
                            '<i class="fa fa-minus-square" aria-hidden="true"></i>'+
                        '</a>'+
                        '<select id="case_select_'+row_id+'" class="search-box pull-right" name="feature" style="height:28px;float:left;">' +
                            '<option>Select feature</option>'
                for(item in data){
                    f_data = f_data + '<option value='+item+'>'+data[item]+'</option>'
                }
                f_data = f_data +'</select>'+
                    '</div>'+
                    '<div id="casecolsm_'+row_id+'" class="col-lg-8" style="padding-right:0;"></div>'+
                    '</div>';
                $("#caseAddFilter").append(f_data);
            }
        });
    }
});

$(document).delegate(".caseMinusRemoveFilter", "click", function (){
    row_id = this.id.split('_')[2];
    div_obj = $(this).parents('div#crow_'+row_id+'.row')
    if (div_obj.length>0){
        div_obj.remove();
        if (row_id == 1){
            prev_obj = $(".diseaseNameSelect").children(".casePlusAddFilter");
        }
        else{
            prev_obj = $("div#crow_"+(row_id-1)+".row .casePlusAddFilter");
        }
        prev_obj[0].disabled = false;
    }
});


var case_plot = function(){
    /* $.blockUI({ message: '<div class="full-width"><img src="/static/img/ajax-loader.gif" /></div> ' });*/
    var case_str = ''
//    {% if job and job.jobs.0.case_sample_id %}
//        case_str = "{{ job.jobs.0.case_sample_id }}"
//    {% else %}
        if ($('#caseSample').DataTable()){
            case_ids = $("#caseSample").DataTable().rows('.selected').data();
            $.each(case_ids, function() {
                case_str = case_str + this[2] + ','
            });
        }
//    {% endif %}
    $("#case_samples").val(case_str);
    case_data = {"cases": case_str};
    $.ajax({
        dataType: "json",
        type: "POST",
        url: "/case_plot",
        data: JSON.stringify(case_data),
        async: false,
        success: function(data){
            Plotly.newPlot('CaseChart', data.graph_data, data.layout);

        }
    });
    /*$.unblockUI();*/

};

$(document).ready(function(){
    case_plot()
    $("#dashboardform").show();

    // AUTOCOMPLETE DISEASE NAME --------------------------------------------------------
    $.ajax({
        url: "/diseases",
        type: "GET",
        dataType: "json",
        success: function (data) {
            $("#case_disease_name").autocomplete({
                source: data,
                minLength: 3,
                select: function(event, ui){
                    $.blockUI({ message: '<div class="full-width"><img src="/static/img/ajax-loader.gif" /></div> ' });
                    var disease = $(this).val().trim();
                    if (disease.length>0){
                        if ($(this).data('columnIndex') == 7){
                            var caseTable = $('#caseSample').DataTable();
                            caseTable.rows('.selected').deselect();
			                caseTable.draw();
                            caseTable.columns(8).search(this.value).draw();
                            var rows = $("#caseSample").dataTable().$('tr', {"filter":"applied"});
                            caseTable.rows(rows).select();
                            case_plot()
                        }
                    }
                    $.unblockUI();
                }
            });
        }
    });


});