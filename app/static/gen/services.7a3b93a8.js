angularApp.controller('ServicesController', ['$scope', '$http', '$window', function($scope, $http, $window) {
    $scope.loading = true;
    $scope.services = [];
    $http.get('/api/services').success(function(response) {
        $scope.loading = false;
        $scope.services = response;
    });
}]);

angularApp.controller('ServiceController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.service = {'internal': false,
                      'builds': [],
                      'building': [],
                      'files': [],
                      'security_groups': [],
                      'hosts': []};
    $scope.currentContainer = 'status';
    $scope.init = function(serviceName) {
        $scope.serviceName = serviceName;
        $http.get('/api/services/' + serviceName).success(function(response) {
            $scope.service = response;
            $scope.serviceUuid = $scope.service.uuid;
            $('.' + $scope.currentContainer).show();
        });
    }
    $scope.changeTab = function(containerName) {
        $('.' + $scope.currentContainer).hide();
        $scope.currentContainer = containerName;
        $('.' + $scope.currentContainer).show();
    };
    $scope.updateService = function() {
        $http.post('/api/services/' + $scope.serviceUuid, $scope.service).success(function(response) {
            $scope.service = response;
        });
    };
    $scope.rows = function(numPerRow, arr) {
        var rows = Math.ceil(arr.length / numPerRow);
        var row_array = new Array();
        for (var i = 0; i < rows + 1; i++) {
            row_array.push(i);
        }
        return row_array;
    };
    $scope.getRowItems = function(numPerRow, row, arr) {
        var return_arr = new Array();
        var start_index = row * numPerRow;
        var end_index = start_index + numPerRow;
        var index = start_index;
        while (index < end_index) {
            if (index < arr.length) {
                return_arr.push(arr[index]);
            }
            index = index + 1;
        }
        return return_arr;
    };
    $scope.createLoadbalancer = function() {
        var $btn = $('#createLB').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/loadbalancer').success(function(response) {
            $scope.service = response;
            $btn.button('reset');
        });
    };
    $scope.updateLoadbalancer = function() {
        var $btn = $('.btn.update-lb').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/loadbalancer/' + $scope.service.loadbalancer.uuid).success(function(response) {
            $scope.service.loadbalancer = response;
            $btn.button('reset');
        });
    };
    $scope.deployLatest = function() {
        $http.post('/api/services/' + $scope.serviceUuid + "/deploy").success(function(response) {
            $scope.service = response;
        });
    };
    $scope.restartService = function() {
        var $btn = $('.btn.restart-service').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/restart').success(function(response) {
            $scope.service = response;
            $btn.button('reset');
        });
    };
}]);
