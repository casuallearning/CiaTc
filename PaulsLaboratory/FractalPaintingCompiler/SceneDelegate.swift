import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = (scene as? UIWindowScene) else { return }

        window = UIWindow(windowScene: windowScene)
        let vanGoghCompilerVC = VanGoghCompilerViewController()
        window?.rootViewController = vanGoghCompilerVC
        window?.makeKeyAndVisible()

        print("🌟 Starry Night computation canvas initialized")
    }
}