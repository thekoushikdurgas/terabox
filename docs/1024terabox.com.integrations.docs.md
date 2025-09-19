logo
Directory
1. Authorization Code Mode

1.0 Overall Process
1.1 Web and Wap Integration Process

1.2 Android Integration Process

1.3 iOS Integration Process

1.4 Server Integration Process

2. Device Code Mode

2.1 Specific Authorization Implementation
2.2 Authorization Service API

2.2.1 Obtaining Device Code and QR Code

3. Basic Capability Integration

3.1. Description
3.2 User Basic Information

3.3 Capacity Related

3.4 File Related

3.5 Share Related

TeraBox Open Platform Integration Document
1. Authorization Code Mode
1.0 Overall Process
Vendors need to provide the application name, product logo, and URL Schemes for both Android and iOS clients.
Vendors need to apply for a client_id and client_secret, as well as a private_secret used to obtain a token.
Guide users to the provided TeraBox page for login authorization. For specific integration processes, see sections 1.1, 1.2, and 1.3.
After successful authorization, obtain the authorization code (code) and proceed to the server-side integration process in section 1.4.
1.1 Web and Wap Integration Process
1.1.1 Parameter Preparation
Obtain client_id: Obtain client_id from TeraBox (requires separate application).
1.1.2 Opening TeraBox Authorization Page in the iframe
Concatenate the web authorization page URL: https://www.terabox.com/wap/outside/login?clientId=XXX, where XXX is the clientId obtained from /:/.
HTML
HTML code demo：
<iframe
    src="https://www.terabox.com/wap/outside/login?clientId=XXX"
    style="width: 375px; height: 667px; position: fixed; top: 10px; left: 50%; transform: translateX(-50%);"
></iframe>

1.1.3 Receiving Authorization Code
JavaScript
JavaScript code demo：

window.addEventListener('message', function (e) {
    try {
        const { data } = e;
        const postData = JSON.parse(data);
        if (postData.event === 'teraboxOauth') {
        // The authorization code can be parsed from data
            console.log('data', postData);
            finishAuth();
        }
    } catch (e) {
        console.log('postmessage error', e);
    }
});

function finishAuth() {
    // remove iframe ...
}

1.2 Android Integration Process
1.2.1 Parameter Preparation
Obtain client_id: Obtain client_id from TeraBox (requires separate application).
1.2.2 Invoking the Login Page
Invoke the system browser via an implicit Intent.
Concatenate the web authorization page URL: https://www.terabox.com/wap/outside/login?clientId=XXX&isFromApp=1, where XXX is the obtained clientId.
Java
Intent browserIntent = new Intent(Intent.ACTION_VIEW,
Uri.parse("https://www.terabox.com/wap/outside/login?clientId=XXX&isFromApp=1"));
startActivity(browserIntent);

1.2.3 Obtaining Login Data
Define scheme and host in the manifest.
Java
<activity android:name=".ui.preview.video.view.yourActivity"
    android:launchMode="singleTask"
    android:exported="true">
    <intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="yourAppName" android:host="teraboxOauth" />
    </intent-filter>
</activity>

Process the login information returned from the browser in the newIntent of the Activity.
Java
public class yourActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIntent(intent);
    }


    private void handleIntent(Intent intent) {
        Uri uri = intent.getData();
        // TODO: handle uri
    }
}

1.3 iOS Integration Process
1.3.1 Parameter Preparation
Obtain client_id: Obtain client_id from TeraBox (requires separate application).
1.3.2 Creating a URL Scheme
Open Xcode, and then open your project.
Select the target for your project.
Click the Info tab.
On the Info page, locate the URL Types section. If you do not see URL Types, you may need to click the + button in the top right corner of the page to add a new project setting.
Click the + button beside URL Types to add a new URL Scheme. Naming convention: app name://teraboxOauth. 
1.3.3 Using System Browser to Open TeraBox Authorization Page
Concatenate the web authorization page URL: https://www.terabox.com/wap/outside/login?clientId=XXX&isFromApp=1, where XXX is the obtained clientId.
OC code example:
objectivec
@import SafariServices;

NSURL *url = [NSURL URLWithString:@"Authorization page URL"];
    
SFSafariViewController *safariVC = [[SFSafariViewController alloc] initWithURL:url];
[self presentViewController:safariVC animated:YES completion:nil];

Swift code example:
Swift
import SafariServices

let authURLString = "Authorization page URL"
guard let url = URL(string: authURLString) else { return }
        
let safariViewController = SFSafariViewController(url: url)
present(safariViewController, animated: true, completion: nil)

1.3.4 Processing the Authorization Result
OC code example
objectivec
// Handling Authorization Login
- (BOOL)application:(UIApplication *)app openURL:(NSURL *)url options:(NSDictionary<UIApplicationOpenURLOptionsKey, id> *)options {
    // Determine whether the login is authorized by terabox
    if ([url.host isEqualToString:@"teraboxOauth"]) {
        // Get the top VC, determine whether it is SFSafariViewController, and remove the top VC
        UIViewController *currentVC = [UIViewController topViewController];
        if ([currentVC isKindOfClass:[SFSafariViewController class]]) {
            [currentVC dismissViewControllerAnimated:YES completion:nil];
        }

        // Get the authorization code
        __block NSString *code = @"";
        NSURLComponents *components = [NSURLComponents componentsWithURL:url resolvingAgainstBaseURL:NO];
        NSArray<NSURLQueryItem *> *queryItems = [components queryItems];

        [queryItems enumerateObjectsUsingBlock:^(NSURLQueryItem * _Nonnull queryItem, NSUInteger idx, BOOL * _Nonnull stop) {
            if ([queryItem.name isEqualToString:@"code"]) {
                code = queryItem.value;
                *stop = YES;
            }
        }];

        NSLog(@"code=%@", code);
    }
}

// Get the top VC
#import <UIKit/UIKit.h>

@interface UIViewController (TopViewController)

+ (UIViewController *)topViewController;

@end

@implementation UIViewController (TopViewController)

+ (UIViewController *)topViewController {
    UIViewController *rootViewController = [UIApplication sharedApplication].keyWindow.rootViewController;
    return [self topViewControllerWithRootViewController:rootViewController];
}

+ (UIViewController *)topViewControllerWithRootViewController:(UIViewController *)rootViewController {
    if ([rootViewController isKindOfClass:[UITabBarController class]]) {
        UITabBarController *tabBarController = (UITabBarController *)rootViewController;
        return [self topViewControllerWithRootViewController:tabBarController.selectedViewController];
    } else if ([rootViewController isKindOfClass:[UINavigationController class]]) {
        UINavigationController *navigationController = (UINavigationController *)rootViewController;
        return [self topViewControllerWithRootViewController:navigationController.visibleViewController];
    } else if (rootViewController.presentedViewController) {
        UIViewController *presentedViewController = rootViewController.presentedViewController;
        return [self topViewControllerWithRootViewController:presentedViewController];
    } else {
        return rootViewController;
    }
}

@end

Swift code example
Swift
func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey : Any] = [:]) -> Bool {
    // Determine whether the login is authorized by terabox
        if let host = url.host(), host == "teraboxOauth" {
            if let topVC = UIViewController.topViewController(), topVC.isKind(of: SFSafariViewController.self) {
                topVC.dismiss(animated: true, completion: nil)
            }
            
        }
        
        // Get the authorization code
        var code = ""
        if let components = URLComponents(url: url, resolvingAgainstBaseURL: false) {
            for queryItem in components.queryItems ?? [] {
                if queryItem.name == "code", let value = queryItem.value {
                    code = value
                    break
                }
            }
        }
        
        print(code)
}


// Get the top VC
import UIKit

extension UIViewController {
    static func topViewController(base: UIViewController? = UIApplication.shared.keyWindow?.rootViewController) -> UIViewController? {
        if let nav = base as? UINavigationController {
            return topViewController(base: nav.visibleViewController)
        } else if let tab = base as? UITabBarController, let selected = tab.selectedViewController {
            return topViewController(base: selected)
        } else if let presented = base?.presentedViewController {
            return topViewController(base: presented)
        } else {
            return base
        }
    }
}

1.4 Server Integration Process
1.4.1 Specific Authorization Implementation
Guide users to the provided TeraBox page for login authorization.
Upon successful authorization, the callback address will return an authorization code (code), which can be used to obtain the access_token.
Use the access_token to obtain the domain name for basic services of the open platform corresponding to this token (Different TeraBox users may correspond to different domain names for basic services of the open platform.). Ultimately, the access_token can be used to access the basic capability services of the open platform. For more details, see section 3 of this document.
If the access_token expires, the refresh_token can be used to refresh the token.
1.4.2 Authorization Service API
1.4.2.1 Exchanging the code for the access_token
API description
Device code mode: After the QR code is provided to a user, this API will be continuously polled via device_code. If the user authorizes by scanning the QR code in the TeraBox app, this API will return an access_token.
Authorization code mode: Use the authorization code (code) returned after the user login authorization to exchange for the access_token.
Notes
The validity period of the access_token is 2 days.
The validity period of the refresh_token is 30 days.
The authorization code (code) can only be used successfully once (In the authorization code mode, the expiration time is 5 minutes).
Request structure
HTTP
POST /oauth/gettoken

Request parameters
Parameter name	Type	Mandatory or not	Example	Description
client_id	string	Yes	Wjaadac3OwQZ7jdalGmB	The AppKey of the application (needs to be applied in advance).
client_secret	string	Yes	VPgfsxBM5kgkeUemwRVmr5AjhFuEV	The SecretKey of the application (needs to be applied in advance).
grant_type	string	Yes	authorization_code	Device code mode: device_code
Authorization code mode: authorization_code
code	string	Yes	57mYYcfS9f	Device code mode: The device_code returned by the /oauth/devicecode API
Authorization code mode: The code returned via callback address after the user authorizes login
timestamp	int64	Yes	1705570481	Current timestamp (in seconds)
sign	string	Yes	asdkkk711UAAK	Dynamic signature (signature rule: md5(“client_id”_“timestamp”_“client_secret”_“private_secret”)), where the private key private_secret should be applied in advance.
Request example
bash
curl --location --request POST 'https://www.terabox.com/oauth/gettoken' \
--form 'client_id="WjY6kfSKgwKB3Ow7jdalGmB"' \
--form 'client_secret="VPgfmrat8UBM5kgUemwRVmr5AjhFuEV"' \
--form 'grant_type="authorization_code"' \
--form 'code="57mYYcfS9f"' \
--form 'timestamp=1705570481' \
--form 'sign="asdkkk711UAAK"' 

Response parameters
Parameter name	Type	Description
data.access_token	string	The obtained access_token, used as the credential to call the TeraBox Open API for accessing user-authorized resources.
data.refresh_token	string	Used to refresh the access_token.
data.expires_in	int	The validity period of the access_token (in seconds).
Error code
Error code	Description
2	Required parameters are missing.
100001	The client_id or client_secret parameter is invalid.
100002	The code is invalid (invalid or expired code).
200001	Unsupported authorization type grant_type.
300001	The frequency of exchanging the code for the access_token is too high.
400001	The user has not yet completed the authorization operation for the device_code (the error code of the device code mode).
500001	Internal service exception.
Response example
json
{
    "data": {
        "access_token": "O4-RcLDmofbh4CXBJIurBiPnsNdM0Xnq5XcPG0jgWIpA98UGBjizeqQ-kQSuRgAZvzPxrg",
        "expires_in": 172800,
        "refresh_token": "sPI60hiSomXZNQzSTHYE9qnRmmRqbwEzqJeqJUXqu4tVVuIOdoRTR9DJkszT1IJC0t6hKQ"
    },
    "errno": 0,
    "newno": "",
    "request_id": 15001987287138667544,
    "server_time": 1700445778,
    "show_msg": ""
}

1.4.2.2 Obtaining access_token Information
API description
TeraBox users in different countries may access the basic services of the open platform through different domain names. Therefore, after obtaining the access_token, you need to obtain the domain name information corresponding to the access_token.

Notes
It is recommended to cache the domain name information corresponding to the access_token, with a caching period of no more than 1 hour. In general, the domain name will not change frequently.

Request structure
HTTP
POST /oauth/tokeninfo

Request parameters
Parameter name	Type	Mandatory or not	Example	Description
access_token	string	Yes	O4-RcLDmofbh4CXBJIurBiPnsNdM0Xnq5XcPG0jgWIpA98UGBjizeqQ-kQSuRgAZvzPxrg	The access_token obtained by the application after authorization.
Request example
bash
curl --location --request POST 'https://www.terabox.com/oauth/tokeninfo' \
--form 'access_token="O4-RcLDmofbh4CXBJIurBiPnsNdM0Xnq5XcPG0jgWIpA98UGBjizeqQ-kQSuRgAZvzPxrg"'

Response parameters
Parameter name	Type	Description
data.client_id	string	The API Key of the application corresponding to the access_token.
data.api_domain	string	The domain name used to request the basic services of the open platform (excluding the /rest/2.0/pcs/superfile2 API).
data.expires_in	int	The validity period of the access_token, in seconds.
data.create_time	int64	The generation time of the access_token (Unix timestamp), in seconds.
data.user_id	int64	The unique ID of the authorized user.
data.upload_domain	string	The domain name used to request the open platform file upload API /rest/2.0/pcs/superfile2.
Error code
Error code	Description
2	Required parameters are missing.
100001	The client_id or client_secret parameter is invalid.
200002	Invalid access_token.
200003	The access_token has expired.
Response example
json
{
    "data": {
        "api_domain": "www.terabox.com",
        "client_id": "WjY6kfSKwKBa3OwQZ7jlGmB",
        "create_time": 1700445778,
        "expires_in": 172800,
        "user_id": 127813130
    },
    "errno": 0,
    "newno": "",
    "request_id": 15002213719900562680,
    "server_time": 1700446200,
    "show_msg": ""
}

1.4.2.3 Refreshing the Access Token
API description
Both the device code and authorization code modes support refreshing the access_token. When the access_token expires, you can use the refresh_token returned in step 2 (/oauth/gettoken) to obtain a new access_token and refresh_token.

Notes
Each refresh_token can be used to refresh and generate new access_token and refresh_token only once. After a successful refresh, the previous access_token will expire in 15 seconds, while the expiration time of the new refresh_token remains the same as the previous one.

Request structure
HTTP
POST /oauth/refreshtoken

Request parameters
Parameter name	Type	Mandatory or not	Example	Description
client_id	string	Yes	WjY6kfawKB3OwQZ7jdalGmB	The AppKey of the application.
client_secret	string	Yes	VPgfmUBM5kgkeUemV	The SecretKey of the application.
refresh_token	string	Yes	sPI60hiSomXZNQzSTHYE9qnRmmRqbw
EzqJeqJUXqu4tVVuIOdoRTR9DJkszT1IJC0t6hKQ	Each refresh_token can be used to refresh the access_token only once. Once the refresh_token has been used to successfully refresh the access_token, it is marked as used and cannot be used again. A new refresh_token is required each time you refresh the access_token.
timestamp	int64	Yes	1705570481	Current timestamp
sign	string	Yes	m5GrSOsOmHafxp8_2bM9	Dynamic signature (same signing rule as for obtaining the sign of the access_token).
Request example
bash
curl --location --request POST 'https://www.terabox.com/oauth/refreshtoken' \
--form 'client_id="WjY6kfSKOwQZ7jdalGmB"' \
--form 'client_secret="abcdfghijk"' \
--form 'refresh_token="sPI60hiSomXZNQzSTHYE9bwEzqJeqJUXqu4tVVuIOdoRTR9DJkszT1IJC0t6hKQ"' \
--form 'timestamp=1705570481' \
--form 'sign="asdkkk711UAAK"'

Response parameters
Parameter name	Type	Description
data.access_token	string	The obtained access_token, used as the credential to call the TeraBox Open API for accessing user-authorized resources.
data.refresh_token	string	Used to refresh the access_token.
data.expires_in	int	The validity period of the access_token, in seconds.
Error code
Error code	Description
2	Required parameters are missing.
100001	The client_id or client_secret parameter is invalid.
200004	Invalid refresh_token.
200005	The refresh_token has expired.
Response example
json
{
    "data": {
        "access_token": "O4-RcLDmofbhJIurBiPnsNdM0Xnq5XcPG0jgWIpA98UGBjizeqQ-kQSuRgAZvzPxrg",
        "expires_in": 172800,
        "refresh_token": "sPI60hiSomXZNQzSE9qnRmmRqbwEzqJeqJUXqu4tVVuIOdoRTR9DJkszT1IJC0t6hKQ"
    },
    "errno": 0,
    "newno": "",
    "request_id": 15001987287138667544,
    "server_time": 1700445778,
    "show_msg": ""
}

2. Device Code Mode
2.1 Specific Authorization Implementation
First, obtain the device code and QR code to proceed with authorization.
Guide users to scan the QR code using TeraBox to complete the authorization operation.
Use the device code to perform a polling operation to exchange it for an access_token.
Use the access_token to obtain the domain name of the corresponding basic services of the open platform. Note that different TeraBox users may correspond to different domain names for basic services of the open platform. With the access_token, you can access the basic capability services provided by the open platform. For details, see section 3 of this document.
If the access_token expires, you can use the refresh_token to refresh the token. The refresh_token is used to obtain a new access_token.
2.2 Authorization Service API
Host
www.terabox.com

Notes
Users need to log in to their account on the TeraBox APP and scan the code to authorize. VPN access is required to log in to the TeraBox APP.

2.2.1 Obtaining Device Code and QR Code
API description
This API is used to obtain the device code and QR code in the device code mode.

Notes
The user code (user_code) and the user code authorization address (verification_url) returned by the API are currently not available.
The QR code returned by the API is in the form of a Base64-encoded string.
The access_token should be exchanged within the expiration time (expires_in) returned by /oauth/devicecode.
The API should be requested at the polling interval (interval) returned by /oauth/devicecode.
Request structure
HTTP
GET /oauth/devicecode

Request parameters
Parameter name	Type	Mandatory or not	Example	Description
client_id	string	Yes	WjY6kfSKwKB3OwQZ7jdalGmB	The AppKey of the application.
Request example
bash
curl -L -X GET 'https://www.terabox.com/oauth/devicecode?client_id=WjY6kfSKwKB3alGmB'

Response parameters
Parameter name	Type	Description
data.device_code	string	Device code, which can be used to generate a one-time access_token.
data.qrcode_url	string	The QR code (a base64-encoded string).
data.expires_in	int	The expiration time of the device_code, in seconds.
The device_code cannot be exchanged for an access_token after expiration.
data.interval	int	The polling interval for exchanging the device_code for an access_token, in seconds.
The polling attempt limit should be less than expire_in/interval.
data.user_code	string	The user code（Currently not available）
If you choose to guide users to authorize by entering the user code, the device needs to display the user code to users.
data.verification_url	string	The URL for users to enter the user code for authorization.（Currently not available）
Error code
Error code	Description
2	Required parameters are missing.
100001	The client_id parameter is invalid.
Response example
json
{
    "data": {
        "device_code": "580uZ7Svrm",
        "expires_in": 300,
        "interval": 2,
        "qrcode_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAa4AAAGuEAAAAAC9DmEFAAAKQUlEQVR4nOzdwXLbvBVA4brzv/8rpwuvyiZDQbgHlNPv28qiaMVnOJM7AP759etfQODfT98A/K3EBRFxQURcEBEXRMQFEXFBRFwQERdExAURcUFEXBARF0TEBRFxQURcEBEXRMQFkX9e+7Gvr/pG/tvq5gPX+7u+f/X1u/vZ/bw7q+9f/feZ/n7urn+1+/vt3t+u1/49PbkgIi6IiAsi4oKIuCAiLoiICyIvzrmupjfBXp1T3P386bnI7v2sXv/6/tU50e793Fm93+l/j6f/Pr95ckFEXBARF0TEBRFxQURcEBEXRN6cc11Nr/e5u/70+qm7602vF5ueM+2uR6vXa929/vQc8mpmTubJBRFxQURcEBEXRMQFEXFBRFwQGZpzPW16TrJ7vel9B6f3WVw1Pdea/vzP5MkFEXFBRFwQERdExAURcUFEXBD5IXOu1fVTq3Oe6X0T735+dz3b9M/vrj+b/n1+5lzrypMLIuKCiLggIi6IiAsi4oKIuCAyNOc6PZeo1zdN7yNYf379+9T7KtbnhT0zN/Pkgoi4ICIuiIgLIuKCiLggIi6IvDnnmj4/afXz7uYWu+dnrX7+9Ourn39V39/u+Wj173/67/P3PLkgIi6IiAsi4oKIuCAiLoiICyJfP3OHuNPnX9XfUr2v4fTcbfX6dz//d/Lkgoi4ICIuiIgLIuKCiLggIi6IROdz1fsI7s5lVu3OberztVbVc63d69dzxjNzOE8uiIgLIuKCiLggIi6IiAsi4oLI0Hqu0+uJdtc7nd538Ol9BKfvZ9fpOeUqcy74aOKCiLggIi6IiAsi4oKIuCDy4pyr3vdvev3XqnqfwNX3r15v9frT67lWP7++n9Pr4X7Pkwsi4oKIuCAiLoiICyLigoi4IPLmvoX1vnTX10+vf3p6PdPT97+7nml1DnZ6brjqve/Dkwsi4oKIuCAiLoiICyLigoi4IBKdz3U3F5jep3B67vPp65HqudzpfRhXP//0vpfv8eSCiLggIi6IiAsi4oKIuCAiLoi8OOfanQvczSXqOdT0eqGn99lbnftdTc8B67+P1fdfPTMH8+SCiLggIi6IiAsi4oKIuCAiLogMnc91Z3fusuvTzp+6U89t6vVQT5+fdvXMHMyTCyLigoi4ICIuiIgLIuKCiLggMnQ+19XpudL03Gd6fdbpff3q87tW73f39929n+m/j9d4ckFEXBARF0TEBRFxQURcEBEXRIbO55o+T+luTnHn9Pqkek40/fNPn5dVn481vZ7sPZ5cEBEXRMQFEXFBRFwQERdExAWRQ/sW3jm9fmn1+k+r1zvVc7RV9fln9ZztmycXRMQFEXFBRFwQERdExAURcUHkxTnX7WU25winz+f69H0B7/zt66E8tG+eXBARF0TEBRFxQURcEBEXRMQFkaF9C6+uc4LTc5Z6H8FP2/dvdz3a6fVyT/89TO8T+XueXBARF0TEBRFxQURcEBEXRMQFkRfnXNP7EK5ef/d+6n0B737+6vQcbvr8sun1WfW/x6qZ63tyQURcEBEXRMQFEXFBRFwQERdEvl77H/x638Hp86Pu/PT1W/X9n14vdVWfB3Zm301PLoiICyLigoi4ICIuiIgLIuKCyJv7Fl6dPg9peu5Ur6+6+mlzuWZfvz+/f9Xu93H3fuu54KOICyLigoi4ICIuiIgLIuKCyIvruf7nbcP7EtZzmXofxTuftp5q9/WrM+ddvX69XTPr0zy5ICIuiIgLIuKCiLggIi6IiAsiL67nOr1eadXTc7fp9VTT+/LV+wjuml4P+Bn7THpyQURcEBEXRMQFEXFBRFwQERdEhvYtvNqdI9Xrv1b3qXt6fdSd3Z+v9xn8afsszsz1PLkgIi6IiAsi4oKIuCAiLoiICyLRnGv6vKOn9zW8u9/p9U1Pz9GeXj+2ev9n5larPLkgIi6IiAsi4oKIuCAiLoiICyIvzrlW5wb1eq7pucm0eu509/r0nPHp9Vf19e9+H+dzwUcRF0TEBRFxQURcEBEXRMQFka/3Jgz1+VvT+9zV539Nrw+7+/ynz6Oa/n1Pn69W/3t98+SCiLggIi6IiAsi4oKIuCAiLoi8OOf62+da9b6Ap+dS9b6Q9flptXp93TdPLoiICyLigoi4ICIuiIgLIuKCyJv7Fk6r99GbPp9pdV/A03O603Omp9dj3dn9fqzngo8iLoiICyLigoi4ICIuiIgLIi/OuZ7eF+9qdW41fb7V3dxkei64e/2n15/Vnz/9/e+u5/vmyQURcUFEXBARF0TEBRFxQURcEHlxznVVz3HuPm917rF6vek50urn717/zu7caPp+p+dSp9//e55cEBEXRMQFEXFBRFwQERdExAWRN+dcV6f35du1ex7X9Pldq6+vqteb7c7BVn/f0+vL3uPJBRFxQURcEBEXRMQFEXFBRFwQGZpzPW16zrRqd1/E1evvzumudtdn7e7zePd5p+eoM/s2enJBRFwQERdExAURcUFEXBARF0R+yJxrem61Ozdavf7uz9frse48fX7X6vtX52j2LYQfRVwQERdExAURcUFEXBARF0SG5lxPz13uXq/XW+1+/p2n7293X8HV9V2rc6jT+x6+xpMLIuKCiLggIi6IiAsi4oKIuCDy5pzrzJzgz56e+6y+f3pONL2P4em5XH0+2J0z+1x6ckFEXBARF0TEBRFxQURcEBEXRL5Or8SC/xeeXBARF0TEBRFxQURcEBEXRMQFEXFBRFwQERdExAURcUFEXBARF0TEBRFxQURcEBEXRP4TAAD//9EkY+Mi8JZjAAAAAElFTkSuQmCC",
        "user_code": "",
        "verification_url": ""
    },
    "errno": 0,
    "newno": "",
    "request_id": 15014880984113383043,
    "server_time": 1700469795,
    "show_msg": ""
}

3. Basic Capability Integration
3.1. Description
1.1 In the offline environment, the HTTP protocol is used, while in the online environment, the HTTPS protocol is used.
1.2 The request domain name is returned by the authorization service’s /oauth/tokeninfo API. The domain name for the file upload (sharded) API /rest/2.0/pcs/superfile2 should be obtained from the upload_domain field, while the domain name for all other basic capability APIs should be obtained from the api_domain field.
1.3 The path parameter related to the file (including the dir parameter for the file list, which means all operations related to the file can only be performed within this space) is fixed as: /From: Other Applications/Application Name-/.
3.2 User Basic Information
3.2.1 User Information API
API address
bash
/openapi/uinfo?access_tokens=ASO9gMfmazGgYCLpLHMzv5zdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA

Request method GET
Request example

bash
curl --location 'https://www.terabox.com/openapi/uinfo?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5zdZ_XH1sIFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA'

Response parameters
Parameter name	Type	Description
uname	string	User nickname
avatar_url	string	Avatar URL
vip_type	int	Premium type: 0: regular user; 1: regular Premium; 2: super Premium
uk	int	User ID
use_type	int	External link activation type: 0: not activated; 1: activated
user_type	int	New/old user type: 0: new user; 1: old user
Response example
json
{
    "avatar_url": "https://dss0.bdstatic.com/7Ls0a8Sm1A5BphGlnYG/sys/portrait/item/netdisk.1.3d20c095.phlucxvny00WCx9W4kLifw.jpg",
    "errmsg": "",
    "errno": 0,
    "request_id": "13855817239228516143",
    "server_time": 1698310870,
    "uk": 4401178462138,
    "uname": "hjy01@t.com",
    "use_type": 0,
    "user_type": 1,
    "vip_type": 0
}

3.2.2 External Link Share Capability Activation
API address
bash
/openapi/active?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5zXH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA

Request method GET
Request example

bash
curl --location 'https://www.terabox.com/openapi/active?access_token=ASO9gMfmazGgYCLpLHMTNQzv5zdZ_XHEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA'

Response parameters
If an activation is successful, errno is 0; otherwise, the activation fails.

Parameter name	Type	Description
order_id	string	Activation order ID (numeric string)
Response example
json
{
    "errno": 0,
    "newno": "",
    "order_id": "77736131208677901",
    "request_id": "104557853518952066",
    "server_time": 1704427908,
    "show_msg": ""
}

3.3 Capacity Related
3.3.1 Capacity Query API
API address
bash
/openapi/api/quota?access_tokens=ASO9gMfmazGgYLHMTNQzv5zdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA

Request method GET
Request example

bash
curl --location 'https://www.terabox.com/openapi/api/quota?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5zdZ_XH1sI1HE9CWbBWWNKSL-Bpo0qROhuwDzeokA'

Response parameters
Parameter name	Type	Description
total	uint64	The total space size, in bytes
used	uint64	The used size, in bytes
Response example
json
{
    "total": 2205465706496,
    "used": 686653888910,
    "errno": 0,
    "request_id": 4890482559098510375
}

3.4 File Related
Overview:
    Uploading a file requires three steps: pre-upload, upload in shards, and creation.
    The first step is pre-upload, which allows you to obtain the uploaded.
    The second step is upload in shards, which requires the uploaded obtained from the first step to perform the sharded upload of the file. The file is divided into multiple smaller parts, which are uploaded one by one.
    The third step is to create a file, which requires merging the multiple shards uploaded in the second step into a complete file.

3.4.1 Pre-upload API
API address
bash
/openapi/api/precreate?access_tokens=ASO9gMfmazGgYCLpLHMTnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA

Request method POST
body Request parameters
Parameter name	Type	Mandatory or not	Description
autoinit	int	Yes	Fixed value 1
block_list	string	Yes	The JSON string of the MD5 array for each file shard.
path	string	Yes	The absolute path of the file used after upload.
Request example
bash
curl --location 'https://www.terabox.com/openapi/api/precreate?access_tokens=ASO9gMfmazGgYCLpLHMTNHEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA' \
--header 'Accept: application/json, text/plain, */*' \
--data-urlencode 'path=/From: Other Device/xxx.txt' \
--data-urlencode 'autoinit=1' \
--data-urlencode 'block_list=["73b4f756c1a2f2ed407e4783966e9189"]'

Response parameters
Parameter name	Type	Description
path	string	The absolute path of the file
uploadid	string	Upload ID
return_type	int	Return type: 1: The file does not exist in the cloud; 2: The file already exists in the cloud.
block_list	[]string	The serial number of the shard to be uploaded, with the index starting from 0.
Response example
json
# When block_list is an empty array, it is equivalent to [0]
{
  "path": "/test/test.zip",
  "uploadid": "N1-MjIwLjE4MS4zOC4xMTY6MTU0NTgxOTIyNzoyNzMzODk2NTI3MzYyMjk2MTU=",
  "return_type": 1,
  "block_list": [0],
  "errno": 0,
  "request_id": 273389652736229615
}
# You need to upload 3 fragments
{
    "path": "/test/test.zip",
    "uploadid": "N1-NjEuMTM1LjE2OS44NDoxNTQ1ODE4MTY1OjgzNDM1NTUyMzU5MjIxMTMzMDc=",
    "return_type": 1,
    "block_list": [0,1,2],
    "errno": 0,
    "request_id": 8343555235922113307
}
# The file already exists in the cloud, upload completed
{
  "return_type": 2,
  "errno": 0,
  "info": {
    "size": 2626327,
    "category": 6,
    "isdir": 0,
    "request_id": 273435691682366413,
    "path": "/test/test.zip",
    "fs_id": 657059106724647,
    "md5": "60bac7b6464d84fed842955e6126826a",
    "ctime": 1545819399,
    "mtime": 1545819399
  },
  "request_id": 273435691682366413
}

3.4.2 File Shard Upload API
Notes:

When multiple shards are uploaded, each shard should be larger than 4 MB; otherwise, this API will return an error. Please ensure that each shard meets the size requirement to avoid errors.
The domain name for the shard upload API should be obtained from the upload_domain field returned by the /oauth/tokeninfo API of the authorization service.
When performing shard uploads, ensure that the order of shards matches the order of shards passed in the blocklist from the pre-upload API (precreate). Ensure the order of shards is correct for subsequent merge operations to proceed correctly.
API address
bash
/rest/2.0/pcs/superfile2?access_tokens=ASO9gMfmazGgYCLpzdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA

Request method POST
Request parameters
Parameters	Type	Description	Mandatory or not
method	string	Fixed to pass upload.	Yes
app_id	int	Fixed to 250528.	Yes
path	string	The absolute path of the uploaded file.	Yes
uploadid	string	The upload ID of the file.	Yes
partseq	int	The location serial number of the file shard, starting from 0.	Yes
body Parameters

Parameters	Mandatory or not	Description
file	Yes	The content of the uploaded file, as a binary byte stream
Request example
bash
curl --location --request POST 'https://c-jp.terabox.com/rest/2.0/pcs/superfile2?method=upload&app_id=250528&path=/From: Other Device/xxx/a.txt&uploadid=N1-MjAyLjIzNC4xOTIuNjc6MTcwMjYzNzU0MjoxODg5MDE2NTAwMjM1NDM2Nw==&partseq=0&access_tokens=ASO9gMfmazGgYCLpLdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA' \
--form 'file=@"/Users/Documents/openapi/a.txt"'

Response parameters
Parameters	Type	Description
md5	string	The MD5 of this shard
uploadid	string	Upload ID
partseq	int	The location serial number of the file shard, starting from 0.
Response example
json
{
  "md5": "73b4f756c1a2f2ed407e4783966e9189",
  "partseq": 0,
  "request_id": 6949704713248675000,
  "uploadid": "N1-MTExLjEwOC4xMTEuMTM3OjE2OTgzOTIwNjY6MzIxNzU0MDQ2NzAxNTU5MjI="
}

3.4.3 File Creation API
API address
bash
/openapi/api/create?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5zdZnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA

Request method POST
body Request parameters
Parameters	Type	Description	Mandatory or not
path	string	The absolute path of the uploaded file.	Yes
size	int64	File Size	Yes
uploadid	string	Upload ID	Yes
block_list	[]string	The JSON string of the MD5s of each file shard should match exactly with the precreate request parameters.	Yes
rtype	int	The file naming policy. The default value is 1.
0: Do not rename. If a file with the same name exists in the cloud, this call will fail and return a conflict;
1: Rename if there is any path conflict;
2: Rename only if there is a path conflict and the block_list is different;
3: Overwrite	Yes
Request example
bash
curl --location 'https://www.terabox.com/openapi/api/create?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5zdZ_XH1sv9CWbBWWNKSL-Bpo0qROhuwDzeokA' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'path=/CloudFile.png' \
--data-urlencode 'size=72990' \
--data-urlencode 'uploadid=N1-MTExLjEwOC4xMTEuMTM0OjE3MDI0NTY0MTI6OTE5MzY0MDQ3NTQwMTI1MTk5Nw==' \
--data-urlencode 'block_list=["84fd2e17018194c18b264048f851ba11"]'

Response parameters
Parameters	Type	Description
fs_id	uint64	The unique identification ID of the file in the cloud
md5	string	The MD5 of the file, only returned when a file is submitted; this value does not exist when a directory is submitted.
server_filename	string	File name
category	int	Category type: 1: video; 2: audio; 3: image; 4: document; 5: application; 6: other; 7: seed
path	string	The absolute path of the file used after upload.
size	uint64	File size, in bytes
ctime	uint64	The file creation time
mtime	uint64	The file modification time
isdir	int	Whether it is a directory: 0: file; 1: directory
from_type	int	
Response example
json
{
    "category": 3,
    "ctime": 1702633080,
    "from_type": 1,
    "fs_id": 934526256472844,
    "isdir": 0,
    "md5": "00a2d1a60t56e3f8f972ff76028d8da7",
    "mtime": 1702633080,
    "path": "/CloudFile_20231215_173800.png",
    "server_filename": "CloudFile_20231215_173800.png",
    "size": 72990,
    "errno": 0,
    "name": "/CloudFile_20231215_173800.png"
}

3.4.4 File Management
API address
bash
/openapi/api/filemanager?access_tokens=ASO9gMfpLHMTNQzv5zdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA

Request method POST
Request parameters
Parameters	Type	Mandatory or not	Description
access_tokens	string	Yes	The API authentication credential
opera	string	Yes	Options include copy, move, rename, and delete.
copy: file copy; move: file movement; rename: file renaming; delete: file deletion
async	int	No	The default value is 0; 0: synchronous; 1: adaptive; 2: asynchronous
The difference lies in whether to care about the success of the request, and the returned structure differs. Different structures are returned based on the request parameters; see the return examples for details.
body Parameters
Parameter name	Type	Mandatory or not	Remarks
filelist	[]json	Yes	See the details below for specific parameters.
bash
# opera=copy
filelist: [{"path":"/hello/test.mp4","dest":"","newname":"test.mp4"}]
# opera=move
filelist: [{"path":"/test.mp4","dest":"/test_dir","newname":"test.mp4"}]
# opera=rename
filelist：[{"path":"/hello/test.mp4","newname":"test_one.mp4"}]
# opera=delete
filelist: ["/test.mp4"]

Request example
bash
curl --location 'https://www.terabox.com/openapi/api/filemanager?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5zdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA&
=2b93b922b918719c4a54147b65d7f2c2&opera=delete'

Response parameters
Parameters	Type	Description
info	array	File information; an empty array is returned when async=2.
taskid	uint64	Asynchronous task ID; returned only when async=2
Response example
json
#When async=0 or 1, the result is returned
{
    "errno": 0,
    "info": [
        {
            "errno": 0,
            "path": "/CloudFile_20231215_173800.png"
        }
    ],
    "request_id": 60168308167642943
}
#When async=2, the result is returned
{
    "errno": 0,
    "info": [],
    "request_id": 60149164342567732,
    "taskid": 257329558616538
}

Error code
Error code	Description
-7	Invalid file name
-8	The file already exists
-9	The file doesn’t exist
3.4.5 Obtaining File List
API address
bash
/openapi/api/list

Request method GET
Request parameters
Parameters	Type	Description	Mandatory or not
access_tokens	string	The identity parameter returned by the authorization API	Yes
path	int	Pagination number	Yes
num	int	Number of items returned per page	Yes
dir	string	The absolute path of the file. It needs to be under the level of /From: Other Device/Application Name - Assigned Application ID/.	Yes
order	string	Sorting field: time (modification time), name (file name), size (size; note that directories do not have a size)	No
desc	int	1: descending order; 0: ascending order	No
web	int	If 1 is passed, the thumbnail field thumbs will be returned.	No
Request example
bash
curl --location 'https://www.terabox.com/openapi/api/list?access_tokens=ASO9naKv9CWbBWWNKSL-Bpo0qROhuwDzeokA&order=time&desc=1&dir=/&num=100&page=1"]'

Response parameters
Parameters	Type	Description
info	json array	File list
info[0][“category”]	int	File type: 1: video; 2: audio; 3: image; 4: document; 5: application; 6: others; 7: seed
info[0][“fs_id”]	uint64	The file ID; the unique identification of the file in the cloud
info[0][“md5”]	string	MD5 of the file
info[0][“local_ctime”]	uint64	The local creation time of the file
info[0][“local_mtime”]	uint64	The local modification time of the file
info[0][“server_ctime”]	uint64	The server-side creation time of the file
info[0][“server_mtime”]	uint64	The server-side modification time of the file
info[0][“server_filename”]	string	The file name on the server
info[0][“size”]	uint64	File Size
info[0][“isdir”]	int	Whether it is a directory
info[0][“path”]	string	The file path
list[0].thumbs	struct	Thumbnail (this structure will not be returned for folders.)
list[0].thumbs.url1	string	Thumbnail URL (140*90)
list[0].thumbs.url2	string	Thumbnail URL (360*270)
list[0].thumbs.url3	string	Thumbnail URL (850*580)
list[0].thumbs.icon	string	Icon
Response example
json
{
    "errno": 0,
    "guid_info": "",
    "list": [
        {
            "tkbind_id": 0,
            "server_filename": "youai_tempDownload_VbMGrjKkFb",
            "category": 6,
            "real_category": "",
            "fs_id": 938083446579468,
            "dir_empty": 0,
            "owner_type": 0,
            "oper_id": 0,
            "server_ctime": 1682140522,
            "play_forbid": 0,
            "wpfile": 0,
            "local_mtime": 1682140522,
            "size": 0,
            "isdir": 1,
            "extent_tinyint7": 0,
            "share": 0,
            "pl": 0,
            "from_type": 0,
            "local_ctime": 1682140522,
            "path": "/youai_tempDownload_VbMGrjKkFb",
            "empty": 0,
            "server_mtime": 1682140522,
            "server_atime": 0,
            "owner_id": 0,
            "thumbs": {
                "icon": "https:\/\/data.terabox.com\/thumbnail\/b5af4baa4ladc9d448c8824eb14bae0b?fid=4401866465594-250528-1013467033118968&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-yuezBcEbFGVY1aRobY0enWSBpMQ%3d&expires=8h&chkbd=0&chkv=0&dp-logid=127002009179710915&dp-callid=0&time=1703037600&size=c60_u60&quality=100&vuk=4401866465594&ft=video",
                "url3": "https:\/\/data.terabox.com\/thumbnail\/b5af4baa4ladc9d448c8824eb14bae0b?fid=4401866465594-250528-1013467033118968&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-yuezBcEbFGVY1aRobY0enWSBpMQ%3d&expires=8h&chkbd=0&chkv=0&dp-logid=127002009179710915&dp-callid=0&time=1703037600&size=c850_u580&quality=100&vuk=4401866465594&ft=video",
                "url2": "https:\/\/data.terabox.com\/thumbnail\/b5af4baa4ladc9d448c8824eb14bae0b?fid=4401866465594-250528-1013467033118968&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-yuezBcEbFGVY1aRobY0enWSBpMQ%3d&expires=8h&chkbd=0&chkv=0&dp-logid=127002009179710915&dp-callid=0&time=1703037600&size=c360_u270&quality=100&vuk=4401866465594&ft=video",
                "url1": "https:\/\/data.terabox.com\/thumbnail\/b5af4baa4ladc9d448c8824eb14bae0b?fid=4401866465594-250528-1013467033118968&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-yuezBcEbFGVY1aRobY0enWSBpMQ%3d&expires=8h&chkbd=0&chkv=0&dp-logid=127002009179710915&dp-callid=0&time=1703037600&size=c140_u90&quality=100&vuk=4401866465594&ft=video"
            },
            "unlist": 0
        }
    ],
    "request_id": 81737848294785966,
    "guid": 0
}

3.4.6 Obtaining File Information
API address
bash
/openapi/api/filemetas

Request method GET
Request parameters
Parameters	Type	Description	Mandatory or not
access_tokens	string	The identity parameter returned by the authorization API	Yes
target	[]string	The absolute path of the file to be queried.
When querying multiple files, use English commas for separation.
The slashes (/) in the path need to be encoded.
For example:[“%2FFrom：Other Device%2FIMG_2023.jpg”,“%2FFrom：Other Device%2SVID_20230815_145833_1.mp4”]	Yes
dlink	int	Whether the download address is required.
0: no; 1: yes. The default value is 0.
Response result; returns dlink, which needs to be URL decoded.	No
Request example
bash
curl --location 'https://www.terabox.com/openapi/api/filemetas?access_tokens=ASO9gMfmYCLpLH5zdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA&target=["%2FSVID_20230815_145833_1.mp4"&dlink=0]'

Response parameters
Parameters	Type	Description
info	json array	File list
info[0][“category”]	int	File type: 1: video; 2: audio; 3: image; 4: document; 5: application; 6: others; 7: seed
info[0][“fs_id”]	uint64	The file ID; the unique identification of the file in the cloud
info[0][“md5”]	string	MD5 of the file
info[0][“local_ctime”]	uint64	The local creation time of the file
info[0][“local_mtime”]	uint64	The local modification time of the file
info[0][“server_ctime”]	uint64	The server-side creation time of the file
info[0][“server_mtime”]	uint64	The server-side modification time of the file
info[0][“filename”]	string	The file name on the server
info[0][“size”]	uint64	File Size
info[0][“duration”]	int	Video file playback duration
info[0][“height”]	int	Video file playback height
info[0][“width”]	int	Video file playback width
info[0][“isdir”]	int	Whether it is a directory.
info[0][“path”]	string	The file path
info[0][“extra_info”]	string	Other video file information
info[0][“dlink”]	string	Download address
info[0]thumbs	struct	Thumbnail
info[0]thumbs.url1	string	Thumbnail URL (140*90)
info[0]thumbs.url2	string	Thumbnail URL (360*270)
info[0]thumbs.url3	string	Thumbnail URL (850*580)
info[0]thumbs.icon	string	Icon
Response example
json
{
    "errno": 0,
    "info": [
        {
            "extent_tinyint4": 0,
            "extent_tinyint1": 0,
            "bitmap": "0",
            "category": 1,
            "fs_id": 1013467033118968,
            "videotag": 0,
            "metadata": "{\"com.android.version\":\"12\",\"creation_time\":\"2023-08-15T06:58:44.000000Z\"}",
            "oper_id": 4401866465594,
            "play_source": 0,
            "play_forbid": 0,
            "wpfile": 0,
            "path_md5": 0,
            "local_mtime": 1695456066,
            "src_location": "tky",
            "share": 0,
            "file_key": "C-I2u5YfkIRQl3uI2AT9HwI26k4pG",
            "errno": 0,
            "local_ctime": 1702440922,
            "extent_tinyint5": 0,
            "sample_rate": 48000,
            "rotate": 0,
            "from_type": 1,
            "height": 1280,
            "id": "1032637",
            "width": 620,
            "privacy": 0,
            "real_category": "",
            "file_size": "4416974",
            "meta_info": "{\"mediaType\":\"video\",\"date_taken\":1692053924,\"has_thumbnail\":true,\"country\":\"JP\"}",
            "upload_type": 2,
            "duration": 10,
            "channels": 1,
            "extra_info": "{\"audio_codec_name\":\"aac\",\"format_name\":\"mov,mp4,m4a,3gp,3g2,mj2\",\"audio_bitrate\":96000,\"video_codec_name\":\"h264\",\"pix_fmt\":\"yuv420p\",\"color_range\":\"tv\",\"color_space\":\"bt709\",\"color_transfer\":\"bt709\",\"color_primaries\":\"bt709\",\"video_bitrate\":3610263,\"video_duration\":9513}",
            "use_segment": 1,
            "server_ctime": 1702440922,
            "resolution": "width:620,height:1280",
            "owner_id": 0,
            "tkbind_id": 0,
            "md5": "cc06043bb48c0ecd38e063e449ebc729",
            "size": 4416974,
            "extent_tinyint3": 0,
            "isdir": 0,
            "owner_type": 0,
            "path": "/SVID_20230815_145833_1.mp4",
            "extent_int3": 4401866465594,
            "frame_rate": 25.859109,
            "extent_tinyint2": 0,
            "server_filename": "SVID_20230815_145833_1.mp4",
            "server_mtime": 1702440922
        }
    ],
    "request_id": 60292865330271632
}

3.4.7 File Search
API address
bash
/openapi/api/search

Request method GET
Request parameters
Parameters	Type	Mandatory or not	Description
access_tokens	string	Yes	The authorization credential
key	string	Yes	Query input value (the file name to be searched).
order	string	No	Sorted by time
page	int	No	Page number, starting from the first page, where the first page equals 1.
num	int	No	Number of entries per page; the default value is 100, with a maximum value of 10,000.
desc	int	No	0: ascending; 1: descending
recursion	int	Yes	Pass 1.
Request example
bash
curl --location 'https://www.terabox.com/openapi/api/search?access_tokens=ASO9gMfmazGgYCLpLHMTzdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA&key=obj_w5zDlMODwrDDiGjCn8K'

Response parameters
Parameters	Type	Description
has_more	int	Whether there is a next page: 0: no; 1: yes
list	json	The returned information as JSON array
list[0][“fs_id”]	uint64	The unique identification ID of the directory in the cloud
list[0][“path”]	string	The absolute path of the file
list[0][“server_filename”]	string	The file name
list[0][“size”]	uint64	File Size
list[0][“server_mtime”]	uint64	The cloud modification time of the file
list[0][“server_ctime”]	uint64	The cloud creation time of the file
list[0][“local_mtime”]	uint64	The client-side modification time of the file
list[0][“local_ctime”]	uint64	The client-side creation time of the file
list[0][“isdir”]	int	Whether it is a directory: 0: file; 1: directory
list[0][“category”]	int	File type: 1: video; 2: audio; 3: image; 4: document; 5: application; 6: others; 7: seed
list[0][“md5”]	string	The MD5 value of the file; this KEY exists if it is a file type.
Response example
bash
{
    "errno": 0,
    "list": [
        {
            "category": 2,
            "delete_type": 0,
            "extent_tinyint1": 0,
            "fs_id": 875963729622734,
            "isdir": 0,
            "local_ctime": 1702792677,
            "local_mtime": 1702792640,
            "md5": "bb290fa11t9db11d44a69dd2e2a89578",
            "oper_id": 4401866465594,
            "owner_id": 0,
            "path": "\/obj_w5zDlMODwrDDiGjCn8Ky_2976638298_b399_5df9_4cc3_e1c53726fa632e5efe23f380f1675396.mp3",
            "server_ctime": 1702792677,
            "server_filename": "obj_w5zDlMODwrDDiGjCn8Ky_2976638298_b399_5df9_4cc3_e1c53726fa632e5efe23f380f1675396.mp3",
            "server_mtime": 1702792677,
            "share": 0,
            "size": 4434477,
            "wpfile": 0
        }
    ],
    "request_id": 60766490708259056,
    "has_more": 0
}

3.4.8 File Download
API address
bash
/openapi/api/download

Request method GET
Request parameters
Parameters	Type	Mandatory or not	Description
access_tokens	string	Yes	The API authorization credential parameters
fidlist	[]uint64	Yes	The ID list of the file to be downloaded (multiple files can be downloaded at the same time, separated by English commas, e.g., [868541097022780,641518032743348]).
type	string	Yes	Fixed to pass dlink.
Request example
bash
curl --location 'https://www.terabox.com/openapi/api/download?access_tokens=ASO9gMfmazGgYCLpLHMTdZ_XH1sI1naKv9CWbBWWNKSL-Bpo0qROhuwDzeokA&fidlist=[934526256472844]&type=dlink&' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
--header 'Connection: keep-alive' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Cookie: xxx'

Response parameters
Parameters	Type	Description
dlink	[]interface	
dlink[0].fs_id	string	The downloaded file ID
dlink[0].dlink	string	The download link corresponding to the file to be downloaded.
(If using this dlink for file download, you need to concatenate the access_tokens request parameters to the returned dlink.For example:https://d.terabox.com/file/84fd2e17018194c18b264048f851ba11?fid=4401866465594-250528-934526256472844&rt=pr&sign=FDtAERVC-DCb740ccc5511e5e8fedcff06b081203-u2yxDGhrYS8wodPxekcedfl0sBU%3D&expires=1h&chkv=1&chkbd=1&chkpc=&dp-logid=20000594728771811&dp-callid=0&dstime=1702641679&r=665553091&vip=2&access_tokens=xxxx)
Response example
bash
{
    "errno": 0,
    "request_id": 20000594728771811,
    "dlink": [
        {
            "fs_id": "934526256472844",
            "dlink": "https:\/\/d.terabox.com\/file\/84fd2e17018194c18b264048f851ba11?fid=4401866465594-250528-934526256472844&rt=pr&sign=FDtAERVC-DCb740ccc5511e5e8fedcff06b081203-u2yxDGhrYS8wodPxekcedfl0sBU%3D&expires=1h&chkv=1&chkbd=1&chkpc=&dp-logid=20000594728771811&dp-callid=0&dstime=1702641679&r=665553091&vip=2"
        }
    ]
}

3.4.9 File Online Playback
API address
bash
/openapi/api/streaming

Request method GET
Request parameters
Parameters	Type	Mandatory or not	Description
access_tokens	string	Yes	The authorization credential
path	string	Yes	The absolute path of the file to be played
type	string	Yes	Stream type: video (M3U8_AUTO_480, M3U8_AUTO_720, M3U8_AUTO_1080); audio (M3U8_MP3_128)
Request example
bash
curl --location 'https://www.terabox.com/openapi/api/streaming?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5zdZ_HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA&path=%2FSVID_20230815_145833_1.mp4&type=M3U8_AUTO_720'

Response parameters
Return the download address corresponding to the m3u8 shard.

Response example
bash
#EXTM3U
#EXT-X-TARGETDURATION:15
#EXT-X-DISCONTINUITY
#EXTINF:10,
https://v1.terabox.com/video/netdisk-videotran-tky/cc06043bb48c0ecd38e063e449ebc729_1075_1_ts/5f6a1f6f3059b8a7e650c014a580a5fa?ts_size=579040&app_id=250528&ccn=JP&csl=0&dp-logid=20048818245753246&fn=SVID_20230815_145833_1.mp4&from_type=1&fsid=1013467033118968&iv=2&logid=20048818245753246&ouk=4401866465594&r=385669310&size=4416974&sta_cs=5&sta_dt=video&sta_dx=4&time=1702670658&to=ze1&tot=ctkov&uo=any&uva=392161200&vuk=4401866465594&dtime=10&etag=5f6a1f6f3059b8a7e650c014a580a5fa&fid=b417b21712b20546ee097f49cad6a0c0-4401866465594&len=579040&path=%2FSVID_20230815_145833_1.mp4&range=0-579039&region=tky&resv4=&sign=BOUTHNF-F3530edecde9cd71b79378b290804a96-hpOx8FK3HRcQkWyYO%252BKJZDj4%252BFA%253D&xcode=32d399fd6bd1c2041fc745ae7b8cbf2fb74c6df737c2fd29d4946cf5815fb144269e0dbd5db9ca20efaf82c4967073620b2977702d3e6764&xv=6&need_suf=&pmk=14005f6a1f6f3059b8a7e650c014a580a5fae198ee3200000008d5e0&by=my-streaming
#EXT-X-ENDLIST

3.5 Share Related
3.5.1 Share Extraction Code Verification
API address
bash
/openapi/share/verify

Request method POST
Request parameters
Parameters	Type	Mandatory or not	Description
access_tokens	string	Yes	The API authorization credential
surl	string	Yes	The short link part of the sharing external link
The format of the sharing external link is https://www.terabox.com/s/1-xxx, only the -xxx part (the part after /s/1) needs to be passed.
body Parameters

Parameter name	Type	Mandatory or not	Description
pwd	string	Yes	Share password; length of 4 characters, consisting of digits + lowercase letters.
Request example
bash
curl --location 'https://www.terabox.com/openapi/share/verify?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5zdZ_I1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA&surl=CcI0dJJ2nzNs9rO6u23QAw'

Response parameters
    Upon successful password verification, a cookie will be set in the response result headers: Set-Cookie BOXCLND. This parameter will be needed for subsequent API request parameters and should be saved.

Parameters	Type	Description
randsk	string	The encrypted extraction code
Response example
json
{
"randsk": {
"+7/8OQAw3auVpJZgEucCFSqJKkFh9zfZXpPbNfn4ja90CrMSighIXd6ku5qhU4qu"
    },
    "errno": 0,
    "request_id": "9143869236641323542",
    "show_msg": "Request Success"
}

Error code
Error code	Description
-12	Error in extraction code
105	External link error
3.5.2 Querying Share Details
API address
bash
/openapi/api/shorturlinfo

Request method GET
Request parameters
Parameters	Type	Description	Mandatory or not
access_tokens	string	The identity parameter returned by the authorization API	Yes
shorturl	string	The sharing short link
The format of the sharing external link is https://www.terabox.com/s/1xxx, only the part after /s/ needs to be passed.	Yes
root	int	The directory. Fixed to pass 1.	Yes
spd	string	The value of the BOXCLND parameter in the Set-Cookie within the headers of the result returned by the /openapi/share/verify authentication extraction code.	Yes
Request example
bash
curl --location 'https://www.terabox.com/openapi/api/shorturlinfo?access_tokens=ASO9gMfmazGgYCLpLHM5zdZ_X1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA&shorturl=1CcI0dJJ2nzNs9rO6u23QAw&root=1'

Response parameters
Parameters	Type	Description
errno	int	Error code
(If an extraction code is set for the external link, it will return -9 if the extraction fails.)
request_id	string	The request identification
show_msg	string	Error information
list	[]struct	The sharing external link information
list.category	string	Classification
list.fs_id	string	File FSID.
list.isdir	string	Whether it is a directory.
list.local_ctime	string	The local creation time
list.local_mtime	string	The local modification time
list.path	string	The path.
list.size	string	File Size
list.server_filename	string	The file name
list.server_ctime	string	The server-side creation time
list.server_mtime	string	The server-side modification time
list.thumbs	struct	Thumbnail
list.thumbs.url1	string	Thumbnail URL (140*90)
list.thumbs.url2	string	Thumbnail URL (360*270)
list.thumbs.url3	string	Thumbnail URL (850*580)
list.thumbs.icon	string	Icon
uk	string	Sharer UK
head_url	string	Sharer avatar information
share_username	string	Sharer username, after desensitization
vip_type	int	Sharer VIP type
shareid	uint64	Share ID
page	int	Share page number
root	int	Whether it is the root directory.
fcount	int	Number of files
Response example
json
{
    "shareid": 1866457029,
    "uk": 4402034215677,
    "dir": "",
    "type": 0,
    "page": 1,
    "root": 1,
    "errno": 0,
    "purchase_forbid_status": 0,
    "head_url": "https:\/\/data.terabox.com\/issue\/netdisk\/ts_ad\/group\/13480498739422554955.png",
    "share_username": "4k***eo",
    "country": "JP",
    "sign": "44674aaf4334be4317ecbde94f60a3945dbe5d41",
    "timestamp": 1700494701,
    "ctime": 1697461920,
    "expiredtype": 0,
    "fcount": 1,
    "uk_str": "4402034215677",
    "vipType": 0,
    "list": [
        {
            "category": "1",
            "fs_id": "758057234722965",
            "isdir": "0",
            "local_ctime": "1655954361",
            "local_mtime": "1655954361",
            "md5": "f04e7a52bd766ebb68fc4191b0915e01",
            "path": "\/gay\/Twisted Thugs #8 - They're from a rough neighborhood and are homosexual.mp4",
            "server_ctime": "1655954362",
            "server_filename": "Twisted Thugs #8 - They're from a rough neighborhood and are homosexual.mp4",
            "server_mtime": "1682254247",
            "size": "1066154301",
            "thumbs": {
                "url1": "https:\/\/data.1024tera.com\/thumbnail\/f04e7a52bd766ebb68fc4191b0915e01?fid=4402034215677-250528-758057234722965&time=1700492400&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-oxUuW0q4yu%2BGgREH6bIC%2FSvZLyE%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=8667047699420974646&dp-callid=0&size=c140_u90&quality=100&vuk=-&ft=video",
                "url2": "https:\/\/data.1024tera.com\/thumbnail\/f04e7a52bd766ebb68fc4191b0915e01?fid=4402034215677-250528-758057234722965&time=1700492400&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-oxUuW0q4yu%2BGgREH6bIC%2FSvZLyE%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=8667047699420974646&dp-callid=0&size=c360_u270&quality=100&vuk=-&ft=video",
                "url3": "https:\/\/data.1024tera.com\/thumbnail\/f04e7a52bd766ebb68fc4191b0915e01?fid=4402034215677-250528-758057234722965&time=1700492400&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-oxUuW0q4yu%2BGgREH6bIC%2FSvZLyE%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=8667047699420974646&dp-callid=0&size=c850_u580&quality=100&vuk=-&ft=video",
                "icon": "https:\/\/data.1024tera.com\/thumbnail\/f04e7a52bd766ebb68fc4191b0915e01?fid=4402034215677-250528-758057234722965&time=1700492400&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-oxUuW0q4yu%2BGgREH6bIC%2FSvZLyE%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=8667047699420974646&dp-callid=0&size=c60_u60&quality=100&vuk=-&ft=video"
            },
            "dlink": ""
        }
    ]
}

Error code
Error code	Description
-9	The request parameter spd is incorrect.
3.5.3 Querying Share File Information
API address
bash
/openapi/share/list

Request method GET
Request parameters
Note：Either dir or root should be passed. If root=1 (indicating the root directory), the dir parameter does not need to be passed; otherwise, the absolute path of the share file should be passed in the dir parameter.

Parameters	Type	Description	Mandatory or not
access_tokens	string	The identity parameter returned by the authorization API	Yes
shorturl	string	The sharing short link
The format of the sharing external link is https://www.terabox.com/s/1xxx, only the xxx part (the part after /s/1) needs to be passed.	Yes
page	int	Pagination number (should be passed when dir is not empty; the pagination parameters are only effective when dir is not the root directory).	Yes
num	int	Number of items returned per page	Yes
sekey	string	The value of the BOXCLND parameter in the Set-Cookie within the headers of the result returned by the /openapi/share/verify authentication extraction code.	Yes
root	int	root=1(indicating the root directory), dir does not need to be passed.	No
dir	string	The share hierarchical directory. An empty value indicates obtaining the first level file list of the external link; If root=1, this field is empty.	No
order	string	asc (ascending), desc (descending); the default value is descending.	No
by	string	Sorting field: time (modification time), name (file name), size (size; note that directories do not have a size); the default value is name.	No
Request example
bash
curl --location 'https://www.terabox.app/openapi/share/list?page=1&num=20&shorturl=-CZRMUjNHP5obASqTLTf8w&root=1&access_tokens=ASO9gMfGgYCLpLHMTNQzv5zdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
--header 'Connection: keep-alive' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Cookie: xxx' 

Response parameters
Parameter name	Type	Description
errno	int	Error code
request_id	string	The request identification
show_msg	string	Error information
share_id	uint64	Share ID
uk	uint64	User UK
list	object	File list
list.category	int	File category
list.fs_id	uint64	File ID
list.isdir	int	0 or 1, indicating whether the file is a directory.
list.local_ctime	uint64	The local creation time
list.local_mtime	uint64	The local modification time
list.md5	string	MD5 of the file
list.path	string	The file path
list.server_ctime	uint64	The server-side creation time
list.server_filename	string	File name
list.server_mtime	uint64	The server-side modification time
list.size	int64	File Size
list.thumbs	struct	Thumbnail
list.thumbs.url1	string	Thumbnail URL (140*90)
list.thumbs.url2	string	Thumbnail URL (360*270)
list.thumbs.url3	string	Thumbnail URL (850*580)
list.thumbs.icon	string	Icon
Response example
json
{
    "cfrom_id": 0,
    "errno": 0,
    "list": [
        {
            "category": 3,
            "emd5": "cacdbeeb9vd70ff5acba3e4cd7f0acb3",
            "fs_id": 165884067459478,
            "isdir": 0,
            "local_ctime": 1689233935,
            "local_mtime": 1689233935,
            "md5": "167cc21acbeefb8c5e5b615cad997b2b",
            "path": "/youai_tempDownload_aISRhDWZeW/youa/web_aISRhDWZeW/co_BtUEAlGlSI.jpg",
            "play_forbid": 0,
            "server_ctime": 1689233935,
            "server_filename": "co_BtUEAlGlSI.jpg",
            "server_mtime": 1689233935,
            "size": 99602,
            "thumbs": {
                "icon": "https://data.terabox.com/thumbnail/167cc21acbeefb8c5e5b615cad997b2b?fid=4399467643166-250528-165884067459478&time=1702792800&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-v%2Bj9MhzVTLCZ7YoZqMFh09zSbFI%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=1317230448&dp-callid=0&size=c60_u60&quality=100&vuk=-&ft=video",
                "url1": "https://data.terabox.com/thumbnail/167cc21acbeefb8c5e5b615cad997b2b?fid=4399467643166-250528-165884067459478&time=1702792800&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-v%2Bj9MhzVTLCZ7YoZqMFh09zSbFI%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=1317230448&dp-callid=0&size=c140_u90&quality=100&vuk=-&ft=video",
                "url2": "https://data.terabox.com/thumbnail/167cc21acbeefb8c5e5b615cad997b2b?fid=4399467643166-250528-165884067459478&time=1702792800&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-v%2Bj9MhzVTLCZ7YoZqMFh09zSbFI%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=1317230448&dp-callid=0&size=c360_u270&quality=100&vuk=-&ft=video",
                "url3": "https://data.terabox.com/thumbnail/167cc21acbeefb8c5e5b615cad997b2b?fid=4399467643166-250528-165884067459478&time=1702792800&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-v%2Bj9MhzVTLCZ7YoZqMFh09zSbFI%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=1317230448&dp-callid=0&size=c850_u580&quality=100&vuk=-&ft=video"
            }
        }
    ],
    "newno": "",
    "request_id": "14772080501474264885",
    "server_time": 1700017544,
    "share_id": 1177027957,
    "show_msg": "",
    "uk": 4399467643166
}

3.5.4 Copying Share Files
API address
bash
/openapi/share/transfer

Request method POST
Request parameters
Parameter name	Type	Mandatory or not	Description
access_tokens	string	Yes	API authentication
shareid	uint64	Yes	External link ID
from	uint64	Yes	The file ID to be copied.
async	int	Yes	Whether to enable asynchronous mode; it is recommended to set it to 2 for full asynchronous processing.
0: synchronous; 1: intelligent asynchronous; 2: asynchronous.
ondup	string	No	File conflict action: fail: failure; newcopy: copy.
sekey	string	Yes	The value of the BOXCLND parameter in the Set-Cookie within the headers of the result returned by the /openapi/share/verify authentication extraction code.
body Parameters
Parameter name	Type	Mandatory or not	Remarks
fsidlist	text	No	The JSON string list of the file fsid to be copied; Either this list or the filelist should be provided.
filelist	text	No	The JSON string list of the file path to be copied. Either this list or the fsidlist should be provided.
path	text	No	Destination directory for copied files; default is the root directory.
Request example
bash
curl --location 'https://www.terabox.app/openapi/share/transfer?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5zdZ_XH1v9CWbBWWNKSL-Bpo0qROhuwDzeokA&jsToken=C88A6D0FC91310EC3CDE0683D6C48BD2AFF21104D5056C5C6ABF3F9F4A6DF2489C702507F0D77575B65AA42ABB5263BF13E94058B83A5347772518883960F2D2&dp-logid=56530200878768330024&async=1&shareid=561062645&from=4402034215677' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
--header 'Connection: keep-alive' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Cookie: xxx' \
--data-urlencode 'fsidlist=["234678677993557"]' \
--data-urlencode 'path=/'

Response parameters
Parameter name	Type	Description
errno	int	Error code
request_id	string	The request identification
show_msg	string	Error information
data	object	The response data
data.task_id	string	Task ID; returns 0 for synchronous mode.
data.tkbind_errno	int	Benefits binding error code (see error code definitions)
Response example
json
{
    "errno": 0,
    "extra": {
        "list": [
            {
                "from": "/Gia Itzel \u0026 BOYFRIEND, LADYBOY.mp4",
                "from_fs_id": 234678677993557,
                "hasVideo": 1,
                "haszip": 0,
                "meta": {
                    "IsDelete": "0",
                    "app_id": "250528",
                    "block_list": [
                        "502de3dc4c60dc74b6e43e46aa0b4b25",
                        "e37824099c871b01c20e22e28b70ea9e",
                        "6951b510579e0421faaa2efa5c7aace6",
                        "bfff483c476c2fe9f2cdb3199f2e8c1c",
                        "7d25f104bd8d691eb54cbb983c25af0a",
                        "f2930fa9781cc27d398347a8f9d8d343",
                        "f79dc1c82925d3e522522633d02b1dd3",
                        "52615c7ea16d702090dc6d05b340f6ec",
                        "992ff8eb29a4e37d9070d2993690e122",
                        "de5fd33c2c394119e216b2a91624c2fa",
                        "9ed38ae0a8dafebd99218c1e7831b6de",
                        "f67c43f6fbb5819927770f374166c4fa",
                        "2280710aa14f43e80b8467d27f50b58d",
                        "9dc2209d449be74c42cae04b55741720",
                        "1919281fb11d11cbb140443938241497",
                        "26bdcc4abdc431203ee2b214a1c0d37e",
                        "46f797fedb8c925fac5d034459d6af7a",
                        "38d83afaa1d7903c74e57616f90ccf3d",
                        "c129febaf300db93aaa9d80085ec3735",
                        "d6612631dca5f9ae0baa765d2e875c35",
                        "ed98c2879f0ce8975a486d5a6a8095e1",
                        "5ea6d77232622477005ee738a6ef3ff9",
                        "d45435f33f5bac8d1f41e439078c3559",
                        "c71da991523ce5179e2b6813c2609003",
                        "bd4a4eba31b9e51107f8508895e55fb7",
                        "ed021775a99a1cff550b608f49e58a09",
                        "54c90cd1db66bd3d37997601b2f8af81",
                        "d1f7138e4a86853315b7b04d854638e0",
                        "77ea31b8ea2d30f4295fb6da4f9993d3",
                        "6518d7773ffb6104a91fbc7a753b298a",
                        "ca26f9f82e1a1801bca06261cb27588d",
                        "60eeb3efe358c8879dd106b74a5189cf",
                        "2c3edc64521f6674f12f4eb99dcf3fe9",
                        "60aa28f85b7daf48947d8895e1e7c2de",
                        "d963174aafc1322315b54d6637fab641",
                        "5e4e47425d23aa3c9d7ebc1c510edb89",
                        "ecc136a0a8ec5e1a17e1e2769b7449e1",
                        "87ffbc7445bbdba3532c93eca0815f0e",
                        "3d275a53fc6b055c211b57b88af7f509",
                        "6c9fd3e66b93f0c8f619bad898358fb6",
                        "c332c6ba97689c5f53d8a8b88e725341",
                        "8d5f9201c2ca57cb6ab9638a0305f0d5",
                        "179f18157a78bdf71e834928a936361c",
                        "b7d10cea7c0d4f2fe4e173202c2b812b",
                        "fdcf7097d149c9a484166829f5068d7f",
                        "1f36c09094f17a97dfcc6f76c924657e",
                        "62c0d99d8ffa6307e802b671bcad5178",
                        "faa26679f5f37dad575d4c0df6a6dcfa",
                        "88627a36d7800d31043edde0d70b4255",
                        "36659297aa02ee1640b976de5f43cab8",
                        "e20cc28f6a253946b16a33c7b35acdf0",
                        "d4919f3a698f7183a9a348d6aa5c6849",
                        "02fcb043d56b49f9ceb95d62474bfd00",
                        "975ada3d96b81131cad8f1b71d03cca6",
                        "9ce1f6c6cdbbbbaab71f6a2c0e8f5e27",
                        "8b4b877fd0da2fa17c29fd567d6439ff",
                        "caae73c51904949ec0649ab9d2ca3ac6",
                        "5d774a822e681f5423838ff82ce061bb",
                        "7482e3442b52d592f4b5fe3d7a8edd9f",
                        "e74bad1582497e24a8dfb2b05a4b0772",
                        "b30d0311502c4ca222e87d7fbeb7ecfd",
                        "3802d3f19462519c20e15563f023e6e4",
                        "a581703225bc8dbbe77a04e0530cf597",
                        "5922e478ad3e0fd1d60bb6271a09a497",
                        "6d4aa48f42e9128c001d0232d85c40a0",
                        "d607d90ca0a7c556b0743154f2bb9d59",
                        "f17d48de937e3278cbdd4c3bd3ab14b3",
                        "5bcb01cd261519d2d35fd9b155fdc6f2",
                        "5e74369edd07234d0ff025d6471eba84",
                        "c25e9bee123ca6838fad99e523141899",
                        "4a3b68058694a2a476200d5d3bfeb430",
                        "6656f50d0fd58e49bce118dc800fc91a",
                        "0c7d58bf154aab55dc5d467a16c7e1f9",
                        "56f2856d75bde51c235ef1e861ed5c35",
                        "b86ca29106483ef9c067c7819f9e4849",
                        "e5a00d43d3a5d73e77e80dc3a67a6d11",
                        "2459dac09c2351c71e315482d82e5fad",
                        "7ddadee78be58ce15e9488b786dd30b2",
                        "d34ed0640eb250aa1eb325222203a32a",
                        "bf6ceef9ce38ede6a1f505a422e6af00",
                        "b64e3324c96098f95c8213cfd7d06112",
                        "43199c000bb6b08e1fcc8289644452a5",
                        "57f5c5aa1c1d44565711d8f5303deb84",
                        "71bfa5cdc532104a11f1e1fa167e6b2b",
                        "f98b379d04256bc83a72d1c72eba1dfb",
                        "c5ee2ead29ceaa45008adf19d04096b5",
                        "185addb56783be7f385df6b9c1ef49eb",
                        "99ae37bf603e4af9a790c5effafdb7b8",
                        "bfc6c2aa824d5fd1ba68b54cea1cc5e5",
                        "a50393e650b04fcd9407c0c7d3a71a72",
                        "c0f362c74fe8dfaa5b04b818637a0b0f",
                        "3fdf9ba15b0ecd4ffa7b4ed74a80e77d",
                        "04ca9f30d48630757cd0df56d58c4fa3",
                        "e6b7f0a2cb201011b14ad04d51c8131d",
                        "eb0546fdcbb53e94e51bdd1a7a046da0",
                        "6389b06a63b4a55befbd8d39577cb376",
                        "9e5b5aaf18ffb2f6573942c1e1d99c34"
                    ],
                    "category": "1",
                    "ctime": "",
                    "delete_fs_id": "0",
                    "extent_int3": "0",
                    "extent_tinyint1": "0",
                    "from_type": "3",
                    "fs_id": "786244936251711",
                    "isdelete": "0",
                    "isdir": "0",
                    "local_ctime": "1655957942",
                    "local_mtime": "1655957942",
                    "md5": "47c40e75fn218183dbc266c7dc3cad82",
                    "mtime": "",
                    "path": "/Gia Itzel \u0026 BOYFRIEND, LADYBOY.mp4",
                    "path_md5": "10381779922534207998",
                    "server_ctime": "1655957942",
                    "server_filename": "Gia Itzel \u0026 BOYFRIEND, LADYBOY.mp4",
                    "server_mtime": "1702798481",
                    "share": "4",
                    "size": "405087436",
                    "status": "0",
                    "tkbind_id": "0",
                    "user_id": "20063839151"
                },
                "to": "/Gia Itzel \u0026 BOYFRIEND, LADYBOY.mp4",
                "to_fs_id": 786244936251711
            }
        ]
    },
    "info": [
        {
            "errno": 0,
            "fsid": "234678677993557",
            "hasVideo": 1,
            "haszip": 0,
            "path": "/Gia Itzel \u0026 BOYFRIEND, LADYBOY.mp4"
        }
    ],
    "newno": "",
    "quantity_limit": 20,
    "request_id": 62091908685133279,
    "show_msg": "",
    "task_id": 0
}

3.5.5 Shared Audio and Video Online Playback
API address
bash
/openapi/share/streaming

Request method GET
Request parameters
Parameters	Type	Description	Mandatory or not
access_token	string	The identity parameter returned by the authorization API	Yes
shareid	uint64	The ID of the share file	Yes
type	string	Stream type: video (M3U8_AUTO_480, M3U8_AUTO_720, M3U8_AUTO_1080); audio (M3U8_MP3_128)	Yes
fid	uint64	The file ID to be queried	Yes
channel	string	Fixed to pass dubox.	Yes
uk	uint64	User encrypted uid	Yes
clienttype	int	Fixed to pass 0.	Yes
sekey	string	The value of the BOXCLND parameter in the Set-Cookie within the headers of the result returned by the /openapi/share/verify authentication extraction code.	Yes
Request example
bash
curl --location 'https://www.terabox.com/openapi/share/streaming?access_tokens=ASO9gMfmazGgYMTNQzv5zdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA'

Response parameters
Return the m3u8 of the video.

Response example
bash
#EXTM3U
#EXT-X-TARGETDURATION:15
#EXT-X-DISCONTINUITY
#EXTINF:10,
https://v1.1024tera.com/video/netdisk-videotran-tky/b2fee89b7dc9760fbc12c8eaf1c1569f_1076_1_ts/c467c93e435b82fff25440450176bdba?ts_size=76521452&app_id=250528&ccn=JP&csl=0&dp-logid=16117799925544529&fn=Big+Cock+Black+Twink+FUCKS+The+Blonde+Leonardo+DiCaprio.mp4&from_type=3&fsid=7438444400937&idc_c=1&isplayer=1&iv=2&logid=16117799925544529&ouk=4402034215677&r=495602772&size=266820896&sta_cs=0&sta_dt=video&sta_dx=254&time=1702656014&to=any&tot=ctkgk&uo=any&uva=198525830&vuk=4401866465594&dtime=10&etag=c467c93e435b82fff25440450176bdba&fid=d384286a88ff5bc6a22211256c932ee6-4401866465594&len=203980&path=%2Fgay%2FBig+Cock+Black+Twink+FUCKS+The+Blonde+Leonardo+DiCaprio.mp4&range=0-203979&region=tky&resv4=&sign=BOUTHNFI-F3530edecde9cd71b79378b290804a96-zlR%252BfS4y6EvPk5lZJfkkebFAwbo%253D&xcode=02bd4caf91cfa3a1ebf13dea32dbdcc0daa2afcc548c2241b8e49ec2ce3f65cc758062bf9dc84c701e392231d0b8f266316128a2cdfcce4d&xv=6&need_suf=&pmk=1400c467c93e435b82fff25440450176bdba3fd2a1170000048f9fec&by=my-streaming
#EXTINF:10,
https://v1.1024tera.com/video/netdisk-videotran-tky/b2fee89b7dc9760fbc12c8eaf1c1569f_1076_1_ts/c467c93e435b82fff25440450176bdba?ts_size=76521452&app_id=250528&ccn=JP&csl=0&dp-logid=16117799925544529&fn=Big+Cock+Black+Twink+FUCKS+The+Blonde+Leonardo+DiCaprio.mp4&from_type=3&fsid=7438444400937&idc_c=1&isplayer=1&iv=2&logid=16117799925544529&ouk=4402034215677&r=495602772&size=266820896&sta_cs=0&sta_dt=video&sta_dx=254&time=1702656014&to=any&tot=ctkgk&uo=any&uva=198525830&vuk=4401866465594&dtime=10&etag=c467c93e435b82fff25440450176bdba&fid=d384286a88ff5bc6a22211256c932ee6-4401866465594&len=3120424&range=203980-3324403&region=tky&resv4=&sign=BOUTHNFI-F3530edecde9cd71b79378b290804a96-zlR%252BfS4y6EvPk5lZJfkkebFAwbo%253D&xcode=02bd4caf91cfa3a1ebf13dea32dbdcc0daa2afcc548c2241b8e49ec2ce3f65cc758062bf9dc84c701e392231d0b8f266316128a2cdfcce4d&xv=6&need_suf=&pmk=1400c467c93e435b82fff25440450176bdba3fd2a1170000048f9fec&by=my-streaming

3.5.6 Meta Information of the External Link Video
API address
bash
/openapi/share/mediameta

Request method GET
Request parameters
Parameters	Type	Description	Mandatory or not
access_token	string	The identity parameter returned by the authorization API	Yes
clienttype	string	Fixed to pass 0.	Yes
uk	string	User encrypted uid	Yes
shareid	uint64	Share ID	Yes
fid	uint64	The ID of the share file to be queried	Yes
sekey	string	The value of the BOXCLND parameter in the Set-Cookie within the headers of the result returned by the /openapi/share/verify authentication extraction code.	Yes
Request example
bash
curl --location 'https://www.terabox.app/openapi/share/mediameta?access_tokens=ASO9gMfmazGgYCLpLHMTNQdZ_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA&clienttype=0&uk=4402034215677&shareid=1866457029&fid=758057234722965&timestamp=1702878367'

Response parameters
Parameters	Type	Description
duration	uint64	Video duration
height	uint64	Video height
width	uint64	Video width
Response example
json
{
    "duration": 6339,
    "errno": 0,
    "height": 720,
    "newno": "",
    "request_id": 83607331382875304,
    "rotate": 0,
    "show_msg": "",
    "width": 1280
}

3.5.7 External Link File Download
API address
bash
/openapi/share/download

Request method GET
Request parameters
Parameters	Type	Mandatory or not	Description
access_token	string	Yes	The API authorization credential parameters
shareid	uint64	Yes	Share ID
fid_list	[]uint64	Yes	The ID list of the file to be downloaded
uk	uint64	Yes	User UK
sekey	string	Yes	The value of the BOXCLND parameter in the Set-Cookie within the headers of the result returned by the /openapi/share/verify authentication extraction code.
Request example
bash
curl --location 'https://www.terabox.app/openapi/share/download?access_tokens=ASO9gMfmazGgYCLpLHMTNQzv5_XH1sI1HEFnaKv9CWbBWWNKSL-Bpo0qROhuwDzeokA'

Response parameters
Parameters	Type	Description
uk	uint64	User UK
sign	string	Signature
shareid	uint64	Share ID
list	[]interface	
list.category	int	File category
list.fid_id	uint64	File ID
list.isdir	int	0 or 1, indicating whether the file is a directory.
list.local_ctime	uint64	The local creation time
list.local_mtime	uint64	The local modification time
list.md5	string	MD5 of the file
list.path	string	The file path
list.server_ctime	uint64	The server-side creation time
list.server_filename	string	File name
list.server_mtime	uint64	The server-side modification time
list.size	uint64	File Size
list.thumbs	struct	Thumbnail
list.thumbs.url1	string	Thumbnail URL (140*90)
list.thumbs.url2	string	Thumbnail URL (360*270)
list.thumbs.url3	string	Thumbnail URL (850*580)
list.thumbs.icon	string	Icon
list.dlink	string	File download link
Response example
json
{
  "shareid": 4017857486,
  "uk": 4400423421256,
  "dir": "",
  "type": 0,
  "prod_type": "share",
  "page": 1,
  "root": 1,
  "third": 0,
  "longurl": "shareid=4017857486&uk=4400423421256",
  "fid": 0,
  "errno": 0,
  "share_username": "tes****111",
  "randsk": "vHWCa%2Fdw6%2BF1YAFMY8%2Bkvt7Q%2BcrZUrFKK9Z2XnLJ0V8%3D",
  "country": "JP",
  "sign": "b35e1d5490e292f1387b0c5ecfa7e6c94fa6c706",
  "timestamp": 1685959414,
  "ctime": 1685706957,
  "expiredtype": 0,
  "fcount": 1,
  "uk_str": "4400423421256",
  "vipType": 0,
  "list": [
    {
      "category": "3",
      "fs_id": "752300820925768",
      "isdir": "0",
      "local_ctime": "1681115603",
      "local_mtime": "1681115603",
      "md5": "8967b0cb6f0ce55656829d0983dc5fca",
      "path": "/zip/SamFrpTool.rar_2023410163319/testModeSam.jpg",
      "server_ctime": "1681115603",
      "server_filename": "testModeSam.jpg",
      "server_mtime": "1681115603",
      "size": "17507",
      "thumbs": {
        "url1": "https://data.4funbox.com/thumbnail/8967b0cb6f0ce55656829d0983dc5fca?fid=4400423421256-250528-752300820925768&time=1685959200&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-6fct%2BGcRdk%2BEfog7lr2CItUOR3s%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=153575299946457365&dp-callid=0&size=c140_u90&quality=100&vuk=-&ft=video",
        "url2": "https://data.4funbox.com/thumbnail/8967b0cb6f0ce55656829d0983dc5fca?fid=4400423421256-250528-752300820925768&time=1685959200&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-6fct%2BGcRdk%2BEfog7lr2CItUOR3s%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=153575299946457365&dp-callid=0&size=c360_u270&quality=100&vuk=-&ft=video",
        "url3": "https://data.4funbox.com/thumbnail/8967b0cb6f0ce55656829d0983dc5fca?fid=4400423421256-250528-752300820925768&time=1685959200&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-6fct%2BGcRdk%2BEfog7lr2CItUOR3s%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=153575299946457365&dp-callid=0&size=c850_u580&quality=100&vuk=-&ft=video",
        "icon": "https://data.4funbox.com/thumbnail/8967b0cb6f0ce55656829d0983dc5fca?fid=4400423421256-250528-752300820925768&time=1685959200&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-6fct%2BGcRdk%2BEfog7lr2CItUOR3s%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=153575299946457365&dp-callid=0&size=c60_u60&quality=100&vuk=-&ft=video"
      },
      "dlink": ""
    }
  ]
}

