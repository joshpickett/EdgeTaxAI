"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.actionAsync = actionAsync;

function _appleUtils() {
  const data = require("@expo/apple-utils");

  _appleUtils = function () {
    return data;
  };

  return data;
}

function _config() {
  const data = require("@expo/config");

  _config = function () {
    return data;
  };

  return data;
}

function _chalk() {
  const data = _interopRequireDefault(require("chalk"));

  _chalk = function () {
    return data;
  };

  return data;
}

function _cliTable() {
  const data = _interopRequireDefault(require("cli-table3"));

  _cliTable = function () {
    return data;
  };

  return data;
}

function _fsExtra() {
  const data = _interopRequireDefault(require("fs-extra"));

  _fsExtra = function () {
    return data;
  };

  return data;
}

function _path() {
  const data = _interopRequireDefault(require("path"));

  _path = function () {
    return data;
  };

  return data;
}

function _xdl() {
  const data = require("xdl");

  _xdl = function () {
    return data;
  };

  return data;
}

function _CommandError() {
  const data = _interopRequireDefault(require("../../CommandError"));

  _CommandError = function () {
    return data;
  };

  return data;
}

function appleApi() {
  const data = _interopRequireWildcard(require("../../appleApi"));

  appleApi = function () {
    return data;
  };

  return data;
}

function _IosApi() {
  const data = require("../../credentials/api/IosApi");

  _IosApi = function () {
    return data;
  };

  return data;
}

function _context() {
  const data = require("../../credentials/context");

  _context = function () {
    return data;
  };

  return data;
}

function _route() {
  const data = require("../../credentials/route");

  _route = function () {
    return data;
  };

  return data;
}

function _IosDistCert() {
  const data = require("../../credentials/views/IosDistCert");

  _IosDistCert = function () {
    return data;
  };

  return data;
}

function _IosProvisioningProfileAdhoc() {
  const data = require("../../credentials/views/IosProvisioningProfileAdhoc");

  _IosProvisioningProfileAdhoc = function () {
    return data;
  };

  return data;
}

function _SetupIosDist() {
  const data = require("../../credentials/views/SetupIosDist");

  _SetupIosDist = function () {
    return data;
  };

  return data;
}

function _SetupIosPush() {
  const data = require("../../credentials/views/SetupIosPush");

  _SetupIosPush = function () {
    return data;
  };

  return data;
}

function _log() {
  const data = _interopRequireDefault(require("../../log"));

  _log = function () {
    return data;
  };

  return data;
}

function _prompts() {
  const data = require("../../prompts");

  _prompts = function () {
    return data;
  };

  return data;
}

function _urlOpts() {
  const data = _interopRequireDefault(require("../../urlOpts"));

  _urlOpts = function () {
    return data;
  };

  return data;
}

function _ora() {
  const data = require("../../utils/ora");

  _ora = function () {
    return data;
  };

  return data;
}

function _clientBuildApi() {
  const data = require("./clientBuildApi");

  _clientBuildApi = function () {
    return data;
  };

  return data;
}

function _generateBundleIdentifier() {
  const data = _interopRequireDefault(require("./generateBundleIdentifier"));

  _generateBundleIdentifier = function () {
    return data;
  };

  return data;
}

function _getRequireWildcardCache(nodeInterop) { if (typeof WeakMap !== "function") return null; var cacheBabelInterop = new WeakMap(); var cacheNodeInterop = new WeakMap(); return (_getRequireWildcardCache = function (nodeInterop) { return nodeInterop ? cacheNodeInterop : cacheBabelInterop; })(nodeInterop); }

function _interopRequireWildcard(obj, nodeInterop) { if (!nodeInterop && obj && obj.__esModule) { return obj; } if (obj === null || typeof obj !== "object" && typeof obj !== "function") { return { default: obj }; } var cache = _getRequireWildcardCache(nodeInterop); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (key !== "default" && Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj.default = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

async function actionAsync(projectRoot, options) {
  var _exp$ios$config, _options$parent;

  const disabledServices = {
    pushNotifications: {
      name: 'Push Notifications',
      reason: 'not yet available until API tokens are supported for the Push Notification system'
    }
  }; // get custom project manifest if it exists
  // Note: this is the current developer's project, NOT Expo Go's manifest

  const spinner = (0, _ora().ora)(`Finding custom configuration for Expo Go...`).start();

  if (options.config) {
    (0, _config().setCustomConfigPath)(projectRoot, options.config);
  }

  const {
    exp
  } = (0, _config().getConfig)(projectRoot, {
    skipSDKVersionRequirement: true
  });

  if (exp) {
    spinner.succeed(`Found custom configuration for Expo Go`);
  } else {
    spinner.warn(`Unable to find custom configuration for Expo Go`);
  }

  if (!exp.ios) exp.ios = {};

  if (!exp.facebookAppId || !exp.facebookScheme) {
    const disabledReason = exp ? `facebookAppId or facebookScheme are missing from app configuration. ` : 'No custom configuration file could be found. You will need to provide a json file with valid facebookAppId and facebookScheme fields.';
    disabledServices.facebookLogin = {
      name: 'Facebook Login',
      reason: disabledReason
    };
  }

  if (!((_exp$ios$config = exp.ios.config) !== null && _exp$ios$config !== void 0 && _exp$ios$config.googleMapsApiKey)) {
    const disabledReason = exp ? `ios.config.googleMapsApiKey does not exist in the app configuration.` : 'No custom configuration file could be found. You will need to provide a json file with a valid ios.config.googleMapsApiKey field.';
    disabledServices.googleMaps = {
      name: 'Google Maps',
      reason: disabledReason
    };
  }

  if (exp.ios.googleServicesFile) {
    const contents = await _fsExtra().default.readFile(_path().default.resolve(projectRoot, exp.ios.googleServicesFile), 'base64');
    exp.ios.googleServicesFile = contents;
  }

  const user = await _xdl().UserManager.getCurrentUserAsync();
  const context = new (_context().Context)();
  await context.init(projectRoot, { ...options,
    allowAnonymous: true,
    nonInteractive: (_options$parent = options.parent) === null || _options$parent === void 0 ? void 0 : _options$parent.nonInteractive
  });
  await context.ensureAppleCtx();
  const appleContext = context.appleCtx;

  if (user) {
    await context.ios.getAllCredentials(context.projectOwner); // initialize credentials
  } // check if any builds are in flight


  const {
    isAllowed,
    errorMessage
  } = await (0, _clientBuildApi().isAllowedToBuild)({
    user,
    appleTeamId: appleContext.team.id
  });

  if (!isAllowed) {
    throw new (_CommandError().default)('CLIENT_BUILD_REQUEST_NOT_ALLOWED', `New Expo Go build request disallowed. Reason: ${errorMessage}`);
  }

  const bundleIdentifier = (0, _generateBundleIdentifier().default)(appleContext.team.id);
  const experienceName = await (0, _clientBuildApi().getExperienceName)({
    user,
    appleTeamId: appleContext.team.id
  });
  const appLookupParams = (0, _IosApi().getAppLookupParams)(experienceName, bundleIdentifier);
  await appleApi().ensureBundleIdExistsAsync(appleContext, appLookupParams, {
    enablePushNotifications: true
  });
  const requestContext = (0, appleApi().getRequestContext)(appleContext);
  const devices = await _appleUtils().Device.getAllIOSProfileDevicesAsync(requestContext);
  const udids = devices.map(device => device.attributes.udid);
  let distributionCert;

  if (user) {
    await (0, _route().runCredentialsManager)(context, new (_SetupIosDist().SetupIosDist)(appLookupParams));
    distributionCert = await context.ios.getDistCert(appLookupParams);
  } else {
    distributionCert = await new (_IosDistCert().CreateIosDist)(appLookupParams.accountName).provideOrGenerate(context);
  }

  if (!distributionCert) {
    throw new (_CommandError().default)('INSUFFICIENT_CREDENTIALS', `This build request requires a valid distribution certificate.`);
  }

  let pushKey;

  if (user) {
    await (0, _route().runCredentialsManager)(context, new (_SetupIosPush().SetupIosPush)(appLookupParams));
    pushKey = await context.ios.getPushKey(appLookupParams);
  }

  let provisioningProfile;
  const createOrReuseProfile = new (_IosProvisioningProfileAdhoc().CreateOrReuseProvisioningProfileAdhoc)(appLookupParams, {
    distCertSerialNumber: distributionCert.distCertSerialNumber,
    udids
  });

  if (user) {
    await (0, _route().runCredentialsManager)(context, createOrReuseProfile);
    provisioningProfile = await context.ios.getProvisioningProfile(appLookupParams);
  } else {
    provisioningProfile = await createOrReuseProfile.createOrReuse(context);
  }

  if (!provisioningProfile) {
    throw new (_CommandError().default)('INSUFFICIENT_CREDENTIALS', `This build request requires a valid provisioning profile.`);
  } // push notifications won't work if we dont have any push creds
  // we also dont store anonymous creds, so user needs to be logged in


  if (pushKey === null || !user) {
    const disabledReason = pushKey === null ? 'you did not upload your push credentials' : 'we require you to be logged in to store push credentials'; // TODO(quin): remove this when we fix push notifications
    // keep the default push notification reason if we haven't implemented API tokens

    disabledServices.pushNotifications.reason = disabledServices.pushNotifications.reason || disabledReason;
  }

  if (Object.keys(disabledServices).length > 0) {
    _log().default.newLine();

    _log().default.warn('These services will be disabled in your custom Expo Go app:');

    const table = new (_cliTable().default)({
      head: ['Service', 'Reason'],
      style: {
        head: ['cyan']
      }
    });
    table.push(...Object.keys(disabledServices).map(serviceKey => {
      const service = disabledServices[serviceKey];
      return [service.name, service.reason];
    }));

    _log().default.log(table.toString());

    _log().default.log('See https://docs.expo.dev/guides/adhoc-builds/#optional-additional-configuration-steps for more details.');
  }

  let email;

  if (user && user.kind === 'user') {
    email = user.email;
  } else {
    var _context$user;

    email = await (0, _prompts().promptEmailAsync)({
      message: 'Please enter an email address to notify, when the build is completed:',
      initial: context === null || context === void 0 ? void 0 : (_context$user = context.user) === null || _context$user === void 0 ? void 0 : _context$user.email
    });
  }

  _log().default.newLine();

  let addUdid;

  if (udids.length === 0) {
    _log().default.log('There are no devices registered to your Apple Developer account. Please follow the instructions below to register an iOS device.');

    addUdid = true;
  } else {
    _log().default.log('Custom builds of Expo Go can only be installed on devices which have been registered with Apple at build-time.');

    _log().default.log('These devices are currently registered on your Apple Developer account:');

    const table = new (_cliTable().default)({
      head: ['Name', 'Identifier'],
      style: {
        head: ['cyan']
      }
    });
    table.push(...devices.map(device => [device.attributes.name, device.attributes.udid]));

    _log().default.log(table.toString());

    const udidPrompt = await (0, _prompts().confirmAsync)({
      message: 'Would you like to register a new device to use Expo Go with?'
    });
    addUdid = udidPrompt;
  }

  const result = await (0, _clientBuildApi().createClientBuildRequest)({
    user,
    appleContext,
    distributionCert,
    provisioningProfile,
    pushKey,
    udids,
    addUdid,
    email,
    bundleIdentifier,
    customAppConfig: exp
  });

  _log().default.newLine();

  if (addUdid) {
    _urlOpts().default.printQRCode(result.registrationUrl);

    _log().default.log('Open the following link on your iOS device (or scan the QR code) and follow the instructions to install the development profile:');

    _log().default.newLine();

    _log().default.log(_chalk().default.green(`${result.registrationUrl}`));

    _log().default.newLine();

    _log().default.log('Please note that you can only register one iOS device per request.');

    _log().default.log("After you register your device, we'll start building your client, and you'll receive an email when it's ready to install.");
  } else {
    _urlOpts().default.printQRCode(result.statusUrl);

    _log().default.log('Your custom Expo Go app is being built! 🛠');

    _log().default.log('Open this link on your iOS device (or scan the QR code) to view build logs and install the client:');

    _log().default.newLine();

    _log().default.log(_chalk().default.green(`${result.statusUrl}`));
  }

  _log().default.newLine();
}
//# sourceMappingURL=clientIosAsync.js.map