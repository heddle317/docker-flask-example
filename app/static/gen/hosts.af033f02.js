angularApp.controller('HostsController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.newHost = true;
    $http.get('/api/images').success(function(response) {
        $scope.imageTypes = response.image_types;
        $scope.imageIDs = response.image_ids;
    });
    $scope.createHost = function() {
        var $btn = $('.host-controller .btn.create').button('loading');
        if ($scope.newHost) {
            var data = {'image_type': $scope.imageType,
                        'image_id': $scope.imageID};
        } else {
            var data = {'host_id': $scope.hostId};
        }
        $http.post('/api/services/' + $scope.serviceUuid + '/hosts', data=data).success(function(response) {
            $scope.service.hosts = response;
        }).finally(function(response) {
            $('#createHostModal').modal('hide');
            $btn.button('reset');
            $scope.hostId = '';
            $scope.imageType = '';
            $scope.imageID = '';
            $scope.newHost = true;
        });
    };
    $scope.updateHost = function(host) {
        var $btn = $('.' + host.uuid + ' .btn.update-host ').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/hosts/' + host.uuid + '/update').success(function(response) {
            $scope.service.hosts = response;
        }).finally(function() {
            $btn.button('reset');
        });
    };
    $scope.terminateHost = function(host) {
        var confirm = $window.confirm("Are you sure you want to delete this host?");
        if (!confirm) {
            return;
        }
        var $btn = $('.' + host.uuid + ' .btn.terminate').button('loading');
        $http.delete('/api/services/' + $scope.serviceUuid + '/hosts/' + host.uuid).success(function(response) {
            $scope.service.hosts = response;
            $btn.button('reset');
        });
    };
    $scope.activateHost = function(host) {
        var $btn = $('.' + host.uuid + ' .btn.activate').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/hosts/' + host.uuid + "/activate").success(function(response) {
            $scope.service.hosts = response;
            $btn.button('reset');
        });
    };
    $scope.deactivateHost = function(host) {
        var $btn = $('.' + host.uuid + ' .btn.deactivate').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/hosts/' + host.uuid + "/deactivate").success(function(response) {
            $scope.service.hosts = response;
            $btn.button('reset');
        });
    };
    $scope.removeService = function(host) {
        var $btn = $('.' + host.uuid + ' .btn.remove-service').button('loading');
        $http.delete('/api/services/' + $scope.serviceUuid + '/hosts/' + host.uuid).success(function(response) {
            $scope.service.hosts = response;
            $btn.button('reset');
        });
    };
}]);

angularApp.controller('RunScriptController', ['$scope', '$http', '$window', '$log', '$timeout', function($scope, $http, $window, $log, $timeout) {
    $scope.newScript = {'name': '',
                        'args': []};
    $scope.currentArg = '';
    $scope.getScripts = function() {
        var $btn = $('.btn.get-scripts').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/scripts/get', data={'password': $scope.password}).success(function(response) {
            $scope.editErrorMessage = '';
            $scope.scripts = response;
            $timeout($scope.closeModal, 30000);
        }).error(function(response) {
            $scope.editErrorMessage = response.message;
        }).finally(function() {
            $scope.password = null;
            $btn.button('reset');
        });
    };
    $scope.runScript = function() {
        var $btn = $('.btn.run-script').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/script', data=$scope.newScript).success(function(response) {
            $scope.newScript = {'name': '',
                                'args': []};
            $scope.currentArg = '';
            $scope.closeModal();
        }).finally(function() {
            $btn.button('reset');
        });
    };
    $scope.closeModal = function() {
        $scope.scripts = null;
        $('#runScriptModal').modal('hide');
    };
    $scope.removeArg = function(arg) {
        var i;
        for (i=0; i < $scope.newScript.args.length; i++) {
            if ($scope.newScript.args[i] == arg) {
                $scope.newScript.args.splice(i, 1);
            }
        }
    };
    $scope.addArg = function() {
        $scope.newScript.args.push($scope.currentArg);
        $scope.currentArg = '';
    };
}]);
