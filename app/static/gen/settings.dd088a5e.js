angularApp.controller('ServicesAttributesController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.password = null;
    $scope.serviceAttributes = null;
    $scope.editAttributes = function() {
        $('#editAttributesModal').modal();
        $scope.newAttribute = {'key': '',
                               'value': '',
                               'attr_type': ''};
    };
    $scope.getServicesAttributes = function() {
        var $btn = $('.btn.get-attrs').button('loading');
        $http.get('/api/services/' + $scope.serviceUuid + '/attributes', {params: {'password': $scope.password}}).success(function(response) {
            $scope.getAttrsErrorMessage = '';
            $scope.serviceAttributes = response;
        }).error(function(response) {
            $scope.getAttrsErrorMessage = response.message;
        }).finally(function() {
            $scope.password = null;
            $btn.button('reset');
        });
    };
    $scope.closeModal = function() {
        $scope.serviceAttributes = null;
        $scope.newAttribute = {'key': '',
                               'value': '',
                               'attr_type': ''};
        $('#editAttributesModal').modal('hide');
    };
    $scope.addAttribute = function(attribute) {
        var $btn = $('.btn.add-attr').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/attributes', data=attribute).success(function(response) {
            $scope.serviceAttributes = response;
            $scope.newAttribute = {'key': '',
                                   'value': '',
                                   'attr_type': ''};
            $btn.button('reset');
        });
    };
    $scope.updateAttribute = function(attribute) {
        var $btn = $('.btn.update-attr').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/attributes/' + attribute.uuid, data=attribute).success(function(response) {
            $scope.serviceAttributes = response;
            $btn.button('reset');
        });
    };
    $scope.deleteAttribute = function(attribute) {
        var confirm = $window.confirm("Are you sure you want to delete this attribute?");
        if (!confirm) {
            return;
        }
        $http.delete('/api/services/' + $scope.serviceUuid + '/attributes/' + attribute.uuid).success(function(response) {
            $scope.serviceAttributes = response;
        });
    };
}]);
