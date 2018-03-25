$(document).ready(function() {

	$("#judulImg").hide()
	$("#hideResultHirarki").hide()
	$("#hasilCluster").hide()

	$.ajax({
		type:'POST',
		url:'getvektor',
		processData: false,
		contentType: false,
		cache: false,
		success : function (data) {
		    if(data.vektor.length >=1) {
			    for (i=0; i < data.vektor.length; i++) {
			      	$('#vektor').append('<option value="'+data.vektor[i][1]+'">'+data.vektor[i][1]+'</option>')
			   	}
			} else {
			    $('#vektor').append('<option value="">Tidak ada data</option>')
			}
		},
		error: function(jqXHR, textStatus, errorThrown){
			alert(textStatus);
		}  
	})

	$('form').on('submit',function(event) {

		event.preventDefault();

		var myId = this.id;
		
		if (myId == 'hirarkiForm') {
			var form_data = new FormData($('#hirarkiForm')[0]);

			$('#step1').attr('class', 'col-xs-2 bs-wizard-step active');

			$.ajax({
				type:'POST',
		      	url:'',
		      	processData: false,
		      	contentType: false,
		      	cache: false,
		      	data : form_data,
		      	success : function (data) {
		   			$('#step1').attr('class', 'col-xs-2 bs-wizard-step complete');

		   			setTimeout(function () {
		   				preproses()
				    }, 2000);
		      	},
		      	error: function(jqXHR, textStatus, errorThrown){
			        alert(textStatus);
			    }  

			})

		} 

		if (myId == 'suggestForm') {

			var form_data = new FormData($('#suggestForm')[0]);
			$.ajax({
				type:'POST',
		      	url:'klustering',
		      	processData: false,
		      	contentType: false,
		      	cache: false,
		      	data : form_data,
		      	success : function (data) {
		      		console.log(data.link)
					$("#suggestLink").attr("href", "/static/img/analisis/hirarki/"+data.link+".png");
					$("#suggestImage").attr("src", "/static/img/analisis/hirarki/"+data.link+".png");

		      	},
		      	error: function(jqXHR, textStatus, errorThrown){
			        alert(textStatus);
			    }  

			})
		}

		if (myId == 'clusterForm') {

			$('#submitCluster').click(function() {
		        $(this).prop('disabled',true);
		    });

			var form_data = new FormData($('#clusterForm')[0]);
			$.ajax({
				type:'POST',
		      	url:'secondcluster',
		      	processData: false,
		      	contentType: false,
		      	cache: false,
		      	data : form_data,
		      	success : function (data) {
		      		console.log(data.formlist)
		      		$("#clusterForm").hide()
		      		$("#hasilCluster").show()
		      	},
		      	error: function(jqXHR, textStatus, errorThrown){
			        alert(textStatus);
			    }  

			})


		}

	});

	

});

function preproses() {
	$('#step2').attr('class', 'col-xs-2 bs-wizard-step active');
	$.ajax({
		type:'POST',
		url:'preproses',
		processData: false,
		contentType: false,
		cache: false,
		dataType: "json",
		success : function (data) {

			$('#step2').attr('class', 'col-xs-2 bs-wizard-step complete');
			setTimeout(function () {
		   		vektorisasi()
			}, 2000);
			

		},
		error: function(jqXHR, textStatus, errorThrown){
			alert(textStatus);
		}  
	})
}

function vektorisasi() {
	$('#step3').attr('class', 'col-xs-2 bs-wizard-step active'); 
	$.ajax({
		type:'POST',
		url:'vektorisasi',
		processData: false,
		contentType: false,
		cache: false,
		dataType: "json",
		success : function (data) {

			$('#step3').attr('class', 'col-xs-2 bs-wizard-step complete');
			setTimeout(function () {
		   		klustering()
			}, 2000);

		},
		error: function(jqXHR, textStatus, errorThrown){
			alert(textStatus);
		}  
	})
}

function klustering() {
	$('#step4').attr('class', 'col-xs-2 bs-wizard-step active'); 
	$.ajax({
		type:'POST',
		url:'klustering',
		processData: false,
		contentType: false,
		cache: false,
		dataType: "json",
		success : function (data) {
			$.ajax({
				type:'POST',
		      	url:'getvektor',
		      	processData: false,
		      	contentType: false,
		      	cache: false,
		      	success : function (data) {
		      		if(data.vektor.length >=1) {
		      			$('#vektor').empty()
			      		for (i=0; i < data.vektor.length; i++) {
			      			$('#vektor').append('<option value="'+data.vektor[i][1]+'">'+data.vektor[i][1]+'</option>')
			      		}
			      	} else {
			      		$('#vektor').append('<option value="">Tidak ada data</option>')
			      	}
		      	},
		      	error: function(jqXHR, textStatus, errorThrown){
			        alert(textStatus);
			    }  

			})
			$('#step4').attr('class', 'col-xs-2 bs-wizard-step complete');
			$('#step5').attr('class', 'col-xs-2 bs-wizard-step active');
			console.log(data.vektor)
			$("#vektorLink").attr("href", "/static/img/analisis/vektor/"+data.vektor+".png");
			$("#vektorImage").attr("src", "/static/img/analisis/vektor/"+data.vektor+".png");
			$("#suggestLink").attr("href", "/static/img/analisis/hirarki/"+data.vektor+".png");
			$("#suggestImage").attr("src", "/static/img/analisis/hirarki/"+data.vektor+".png");
			setTimeout(function () {
				$("#menuHirarki").hide()
		   		$("#judulImg").show()
				$("#hideResultHirarki").show()
			}, 2000);
		},
		error: function(jqXHR, textStatus, errorThrown){
			alert(textStatus);
		}  
	})
}

