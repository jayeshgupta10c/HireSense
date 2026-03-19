/**
 * controllers/upload.controller.ts — FIXED
 * Fixes: file select broken, async/$apply conflicts
 */
declare var angular: any;

angular.module("hireSenseApp").controller(
  "UploadController",
  ["$scope", "$rootScope", "$timeout",
  function ($scope: any, $rootScope: any, $timeout: any) {

    // ── State ──────────────────────────────────────────────────────────────
    $scope.uploadQueue   = [];
    $scope.uploadResults = [];
    $scope.uploading     = false;
    $scope.uploadError   = "";
    $scope.dragOver      = false;

    // ── File input — called via id-based listener set up in $onInit ────────
    // Exposed on scope so the HTML inline onchange can reach it safely
    $scope.handleFileInput = function (inputEl: HTMLInputElement) {
      var files = Array.prototype.slice.call(inputEl.files || []);
      $scope._addFiles(files);
      inputEl.value = "";
      // Must manually trigger digest since we came from a native DOM event
      if (!$scope.$$phase) { $scope.$apply(); }
    };

    // ── Drag & Drop ────────────────────────────────────────────────────────
    $scope.onDragOver = function (event: DragEvent) {
      event.preventDefault();
      if (!$scope.dragOver) {
        $scope.dragOver = true;
        if (!$scope.$$phase) { $scope.$apply(); }
      }
    };

    $scope.onDragLeave = function () {
      $scope.dragOver = false;
      if (!$scope.$$phase) { $scope.$apply(); }
    };

    $scope.onDrop = function (event: DragEvent) {
      event.preventDefault();
      $scope.dragOver = false;
      var files = Array.prototype.slice.call(
        (event.dataTransfer && event.dataTransfer.files) ? event.dataTransfer.files : []
      );
      $scope._addFiles(files);
      if (!$scope.$$phase) { $scope.$apply(); }
    };

    // ── Add files to queue ─────────────────────────────────────────────────
    $scope._addFiles = function (files: File[]) {
      var allowed = ["pdf", "txt", "doc"];
      files.forEach(function (f: File) {
        var ext = f.name.split(".").pop()!.toLowerCase();
        if (allowed.indexOf(ext) !== -1) {
          var exists = $scope.uploadQueue.some(function (q: File) {
            return q.name === f.name && q.size === f.size;
          });
          if (!exists) { $scope.uploadQueue.push(f); }
        }
      });
    };

    $scope.removeFromQueue = function (index: number) {
      $scope.uploadQueue.splice(index, 1);
    };

    // ── Upload — uses .then() chains to avoid async/await + $apply clashes ─
    $scope.uploadAll = function () {
      if (!$scope.uploadQueue.length) { return; }

      $scope.uploading     = true;
      $scope.uploadError   = "";
      $scope.uploadResults = [];

      var api   = (window as any).ApiService;
      var queue = $scope.uploadQueue.slice(); // snapshot
      var index = 0;

      function uploadNext() {
        if (index >= queue.length) {
          // All done
          $scope.uploadQueue = [];
          $scope.uploading   = false;
          $rootScope.$broadcast("resumes:updated");
          if (!$scope.$$phase) { $scope.$apply(); }
          return;
        }

        var file = queue[index++];
        api.uploadResume(file).then(function (res: any) {
          $scope.uploadResults.push({ success: true, name: file.name, resume: res.resume });
          if (!$scope.$$phase) { $scope.$apply(); }
          uploadNext();
        }).catch(function (err: any) {
          $scope.uploadResults.push({ success: false, name: file.name, error: err.message });
          if (!$scope.$$phase) { $scope.$apply(); }
          uploadNext();
        });
      }

      uploadNext();
    };

    // ── Format helpers ─────────────────────────────────────────────────────
    $scope.formatSize = function (bytes: number): string {
      if (bytes < 1024) { return bytes + " B"; }
      if (bytes < 1048576) { return (bytes / 1024).toFixed(1) + " KB"; }
      return (bytes / 1048576).toFixed(1) + " MB";
    };
  }]
);