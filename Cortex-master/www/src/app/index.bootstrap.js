'use strict';

// index.html page to dist folder
import '!!file-loader?name=[name].[ext]!../cynox_logo.svg';

import '../assets/images/logo-dark.png';

// vendor files
import './index.vendor';

// main App module
import './index.module';

import '../assets/styles/sass/index.scss';

angular.element(document).ready(() => {
  angular.bootstrap(document, ['cortex'], {
    strictDi: true
  });
});
