$(document).ready(function() {
	$(".refresh").on('click', function(e) {
		refresh_values(e);
		fill_out_sensor_list();
	});
	fill_out_sensor_list();
	$(".refresh").click();
	$("#status-form,#sensor-form").submit(function(event) {
	    // Ajax Put
	    event.preventDefault();
		data = $(this).serialize();
		url = this.action;
		my_href = $(this).data('href');
		$.ajax({
            url: this.action,
            method: this.method,
            data: data,
            dataType: "json"
		}).done(function(data){
		    if(data['success']===true) {
		        $(".refresh").click();
		        window.location.href = my_href;
		    } else {
		        printError("Error")
		    }
		});

	});
});

function printError(message) {
    alert(message)
}

function refresh_values(e) {
	var url = e.target.href;
	var list = $(e.target).siblings('.data');
	var my_class = String($(e.target).parent().attr('id'))
	$.ajax({
		url: url,
		dataType: "json"
	}).done(function(data){
		list.empty();
		// iterating through array
		$.each(data, function(key, value) {
			var appended = to_list(value, my_class);
			list.append(appended)
		})
	})
	e.preventDefault();
}

function fill_out_sensor_list() {
	$.ajax({
		url: "/api/sensor",
		dataType: "json"
	}).done(function(data){
		// iterating through array
		$('#sensor-mapping').empty();
		$.each(data, function(key, value) {
			var string = '<option value="' + value['id'] + '">' + value['id'] + ' - ' + value['name'] + '</option>';
			$('#sensor-mapping').append(string)
		})
	})
}

function remove_value(e) {
	var url = e.target.href;
	$.ajax({
		url: url,
		dataType: "json",
		method: "DELETE"
	}).done(function(data){
	    if(data['message']) {
		    printError(data['message'])
		}
		$(".refresh").click();

	})
	e.preventDefault();
}

function show_value(e) {
	var url = e.target.href;
	$.ajax({
		url: url,
		dataType: "json",
		method: "GET"
	}).done(function(data){
		alert(data[0]['value'])
	})
	e.preventDefault();
}

function to_list(value, my_class) {
    var ul = $('<ul class="item-list"></ul>');
    var id = value['id']
	if(my_class === "status") {
		ul.append('<li class="get-value-container"><a href="api/status?id=' + id + '&request=1" onclick="show_value(event);" class="get-value"><i class="fa fa-get-pocket" aria-hidden="true"></i>Get Value</a></li>')
	}
	ul.append('<li class="remove-container"><a href="/api/' + my_class + '?id=' + id + '" onclick="remove_value(event);" class="remove"><i class="fa fa-times" aria-hidden="true"></i>Remove</a></li>')
	$.each(value, function(key, value) {
		ul.append('<li><div class="upper">' + key + '</div><div class="down">' + value + '</div></li>');
	})

	var _return = '<li>'+ul[0].outerHTML+'</li>';
	return _return;
}


