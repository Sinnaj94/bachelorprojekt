function removeItem(item) {
	toggleClass(item,'validation');
	toggleTopbar(true, true);
}


function toggleClass(item, classname) {
	if(item.classList.contains(classname)) {
		item.classList.remove(classname);
	} else {
		item.classList.add(classname);
	} 
}


function toggleTopbar(state, from_delete) {
	var object = document.querySelector('#my-topbar');
	state? object.classList.add('topbar-active'): object.classList.remove('topbar-active');
	from_delete? document.querySelector('#my-topbar .delete').classList.remove('inactive') : document.querySelector('#my-topbar .delete').classList.add('inactive')
}

function deleteMe() {
	objects = document.querySelectorAll('.validation');
	objects.forEach(item => {
		var _id= $(item).closest(".modify").data('id');
		$.ajax({
		    url: '/api/status/'+_id,
		    type: 'DELETE',
		    success: function(result) {
		        var _li = $(item).closest("li");
	        	_li.remove();
		    }
		});
	})
	toggleTopbar(false, true)
}

function removeValidationState() {
	var selected = document.querySelectorAll('.validation');
	selected.forEach(item =>{
		item.classList.remove('validation');
	});
}


function finished() {
	toggleTopbar(false, false);
	removeValidationState()
}

function displayModalLayer() {
	$('.outer-container *:not(#modal_layer):not(#modal_layer *)').addClass('blur')
	$('#modal_layer').attr('data-visible', true);
}

function closeModalLayer(element) {
	if($(element).hasClass('finished')) {
		validateAndAdd();
	} else {
		$('.outer-container *:not(#modal_layer):not(#modal_layer *)').removeClass('blur')
		$('#modal_layer').attr('data-visible', false);
	}
}

function validateAndAdd() {
	if(isValid()) {
		var data = $('#modal-form').serialize();
		addItem(data);
		$('.outer-container *:not(#modal_layer):not(#modal_layer *)').removeClass('blur')
		$('#modal_layer').attr('data-visible', false);
	} else {
		alert("Validate your fields please.")
	}
}

function isValid() {
	var _return = true;
	$('#modal-attributes li input').each(function(index) {
		if(!$(this).val()) {
			_return = false;
		}
	});
	return _return;
}

function addItem(data) {
	$.ajax({
	    url: '/api/status',
	    type: 'POST',
	    data: data,
	    success: function(result) {
	    	appendToDom(result);
	    }
	});
} 

function appendToDom(object) {
	var appended_item = `<li><div class="list-container"><div class="list-title">${object.name} <div class="subtext">${object.description}</div></div><div class="modify" data-id="${object.id}"><i class="material-icons edit">create</i><i class="material-icons remove" onclick="removeItem(this)">remove</i></div></div></li>`
	$(appended_item).insertBefore($('#add_item')).slideDown();
} 

function abort() {
	toggleTopbar(false, false);
	removeValidationState()
}

function appendToModalLayer(item,result) {
	var inputType = '';
	if(result instanceof Array) {
		inputType = getAsSelect(result);
	} else if(result === "String") {
		inputType = "<input type='text'>";
	} else if(result === "int") {
		inputType = "<input type='number'>";
	}
	inputType = $(inputType).attr('name', item).prop('outerHTML');
	$('#modal-attributes').append(`<li name="${item}" class="list-input"><span>${item}</span>${inputType}</li>`);

}

function getAsSelect(result) {
	var _return = $('<select></select>');
	result.forEach(item => {
		_return.append($(`<option value="${item}">${item}</option>`));
	})
	return _return.prop('outerHTML');
}

function addAdditionalAttributes() {
	$.ajax({
	    url: '/api/configuration/statusobject',
	    type: 'GET',
	    success: function(result) {
	    	for(item in result) {
	    		appendToModalLayer(item, result[item]);
	    	}
	    }
	});
}

$(document).ready(addAdditionalAttributes());

