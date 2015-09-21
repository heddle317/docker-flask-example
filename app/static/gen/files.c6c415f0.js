angularApp.controller('FileController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.currentFile = null;
    $scope.password = null;
    $scope.addFile = function(file) {
        var $btn = $('.btn.add-file').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/files', data=file).success(function(response) {
            $scope.service.files = response;
            $btn.button('reset');
            $scope.closeModal();
        });
    };
    $scope.createFile = function() {
        $scope.newFile = {'name': '',
                          'body': '',
                          'mode': ''};
        $('#newFileModal').modal();
    };
    $scope.editFile = function(file) {
        $('#editFileModal').modal();
        $scope.fileUuid = file.uuid;
    };
    $scope.getFile = function() {
        var $btn = $('.btn.get-file').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/files/' + $scope.fileUuid + '/get', data={'password': $scope.password}).success(function(response) {
            $scope.editErrorMessage = '';
            $scope.currentFile = response;
        }).error(function(response) {
            $scope.editErrorMessage = response.message;
        }).finally(function() {
            $scope.password = null;
            $btn.button('reset');
        });
    };
    $scope.closeModal = function() {
        $window.location.reload();
    };
    $scope.updateFile = function(file) {
        var $btn = $('.btn.update-file').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/files/' + file.uuid, data=file).success(function(response) {
            $scope.service.files = response;
            $btn.button('reset');
            $scope.closeModal();
        });
    };
    $scope.openDeleteModal = function(file) {
        $scope.delFile = file;
        $('#deleteFileModal').modal('show');
    };
    $scope.deleteFile = function(file) {
        var $btn = $('.btn.delete-file').button('loading');
        $http.post('/api/services/' + $scope.serviceUuid + '/files/' + file.uuid + '/delete', params={'password': $scope.password}).success(function(response) {
            $scope.service.files = response;
            $window.location.reload();
        }).error(function(response) {
            $scope.editErrorMessage = response.message;
        }).finally(function() {
            $scope.password = null;
            $btn.button('reset');
        });
    };
    $scope.closeDeleteModal = function() {
        $scope.delFile = null;
        $('#deleteFileModal').modal('hide');
    };
    $scope.deployServiceFiles = function() {
        $http.post('/api/services/' + $scope.serviceUuid + "/files/deploy").success(function(response) {
        });
    };
}]);
