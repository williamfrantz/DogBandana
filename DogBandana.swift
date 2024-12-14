import Cocoa

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Create the window
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 800, height: 600),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        
        // Set up the content
        let library = ImageLibrary(directory: "/Users/wfrantz/bin/Dog Bandana/Assets")
        let galleryViewController = ImageGalleryViewController(library: library)
        window?.contentViewController = galleryViewController
        
        // Configure the window
        window?.title = "Dog Bandana"
        window?.center()
        window?.makeKeyAndOrderFront(nil)

        // Set up the main menu
        setupMainMenu()

        // Ensure the app is active and brought to front
        NSApp.activate(ignoringOtherApps: true)
    }

    private func setupMainMenu() {
        let mainMenu = NSMenu()
        
        // Application Menu (DogBandana)
        let appMenuItem = NSMenuItem()
        let appMenu = NSMenu()
        
        // About item
        let aboutItem = NSMenuItem(title: "About DogBandana", 
                                 action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), 
                                 keyEquivalent: "")
        
        // Hide DogBandana
        let hideItem = NSMenuItem(title: "Hide DogBandana", 
                                action: #selector(NSApplication.hide(_:)), 
                                keyEquivalent: "h")
        
        // Hide Others
        let hideOthersItem = NSMenuItem(title: "Hide Others", 
                                      action: #selector(NSApplication.hideOtherApplications(_:)), 
                                      keyEquivalent: "h")
        hideOthersItem.keyEquivalentModifierMask = [.command, .option]
        
        // Show All
        let showAllItem = NSMenuItem(title: "Show All", 
                                   action: #selector(NSApplication.unhideAllApplications(_:)), 
                                   keyEquivalent: "")
        
        // Separator
        let separatorItem = NSMenuItem.separator()
        
        // Quit
        let quitItem = NSMenuItem(title: "Quit DogBandana", 
                                action: #selector(NSApplication.terminate(_:)), 
                                keyEquivalent: "q")
        
        // Add items to app menu
        appMenu.addItem(aboutItem)
        appMenu.addItem(NSMenuItem.separator())
        appMenu.addItem(hideItem)
        appMenu.addItem(hideOthersItem)
        appMenu.addItem(showAllItem)
        appMenu.addItem(separatorItem)
        appMenu.addItem(quitItem)
        
        // Add app menu to main menu
        appMenuItem.submenu = appMenu
        mainMenu.addItem(appMenuItem)
        
        // File Menu
        let fileMenuItem = NSMenuItem()
        let fileMenu = NSMenu(title: "File")
        
        // Close Window
        let closeItem = NSMenuItem(title: "Close Window", 
                                 action: #selector(NSWindow.performClose(_:)), 
                                 keyEquivalent: "w")
        fileMenu.addItem(closeItem)
        
        fileMenuItem.submenu = fileMenu
        mainMenu.addItem(fileMenuItem)
        
        // Edit Menu (for copy/paste operations)
        let editMenuItem = NSMenuItem()
        let editMenu = NSMenu(title: "Edit")
        
        editMenu.addItem(withTitle: "Copy", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        editMenu.addItem(withTitle: "Paste", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        editMenu.addItem(withTitle: "Select All", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
        
        editMenuItem.submenu = editMenu
        mainMenu.addItem(editMenuItem)
        
        // Set the main menu
        NSApplication.shared.mainMenu = mainMenu
    }
    
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
}

// Rest of your classes (ImageLibrary, ImageGalleryViewController, etc.) go here

// MARK: - Graphic Class
class Graphic {
    private let defaultSize = NSSize(width: 16 * 30, height: 9 * 30)
    private let defaultThumbnailSize = NSSize(width: 128, height: 128)
    private let scaleFactor: CGFloat = 0.60
    
    private var filename: String?
    private var image: NSImage?
    private var thumbnail: NSImage?
    private var thumbnailSize: NSSize?
    private var text: String?
    private var font: NSFont?
    private var fontSize: CGFloat?
    private var targetSize: NSSize?
    private var basename: String?
    
    init(filename: String? = nil, text: String? = nil, size: NSSize? = nil) {
        if let filename = filename {
            setFilename(filename)
        }
        if let text = text {
            setText(text)
        }
        if let size = size {
            setSize(size)
        }
    }
    
    func setFilename(_ filename: String) {
        self.filename = filename
        self.basename = (filename as NSString).lastPathComponent
    }
    
    func setText(_ text: String) {
        guard self.text != text else { return }
        self.text = text
        self.image = nil
    }
    
    func setSize(_ size: NSSize? = nil) {
        let newSize = size ?? defaultSize
        guard targetSize != newSize else { return }
        targetSize = newSize
        image = nil
    }
    
    func getImage(size: NSSize? = nil) -> NSImage? {
        if let size = size {
            setSize(size)
        }
        
        if let image = image {
            return image
        }
                
        return loadImage()
    }
    
    private func loadImage() -> NSImage? {
        guard let filename = filename else { return nil }
        image = NSImage(contentsOfFile: filename)
        return image
    }
    
    private func createTextImage() -> NSImage? {
        guard let text = text,
              let targetSize = targetSize else { return nil }
        
        // Create a new image context
        let image = NSImage(size: targetSize)
        image.lockFocus()
        
        // Find appropriate font size
        var fontSize: CGFloat = 500
        while !canTextFit(fontSize: fontSize) && fontSize > 10 {
            fontSize -= 10
        }
        
        guard let font = NSFont(name: "Helvetica", size: fontSize) else {
            image.unlockFocus()
            return nil
        }
        
        let attributes: [NSAttributedString.Key: Any] = [
            .font: font,
            .foregroundColor: NSColor.black
        ]
        
        let textSize = text.size(withAttributes: attributes)
        let rect = NSRect(x: (targetSize.width - textSize.width) / 2,
                         y: (targetSize.height - textSize.height) / 2,
                         width: textSize.width,
                         height: textSize.height)
        
        text.draw(in: rect, withAttributes: attributes)
        image.unlockFocus()
        
        self.image = image
        return image
    }
    
    private func canTextFit(fontSize: CGFloat) -> Bool {
        guard let text = text,
              let targetSize = targetSize,
              let font = NSFont(name: "Helvetica", size: fontSize) else { return false }
        
        let attributes: [NSAttributedString.Key: Any] = [.font: font]
        let textSize = text.size(withAttributes: attributes)
        
        return textSize.width <= targetSize.width * scaleFactor &&
               textSize.height <= targetSize.height * scaleFactor
    }
}

// MARK: - ImageLibrary Class
class ImageLibrary {
    private let imageExtensions = ["png", "jpg", "jpeg", "tiff", "bmp", "gif"]
    private let fontExtensions = ["ttf", "otf", "ttc"]
    
    private var graphicList: [Graphic] = []
    private var directory: String
    private var thumbnailSize = NSSize(width: 128, height: 128)
    
    init(directory: String, text: String? = nil, size: NSSize? = nil) {
        self.directory = directory
        
        let fileManager = FileManager.default
        guard let files = try? fileManager.contentsOfDirectory(atPath: directory) else { return }
        
        for filename in files {
            let fullPath = (directory as NSString).appendingPathComponent(filename)
            let ext = (filename as NSString).pathExtension.lowercased()
            
            if text != nil {
                // If text is provided, we're looking for fonts
                if fontExtensions.contains(ext) {
                    let graphic = Graphic(filename: fullPath, text: text, size: size)
                    graphicList.append(graphic)
                }
            } else {
                // If no text is provided, we're looking for images
                if imageExtensions.contains(ext) {
                    let graphic = Graphic(filename: fullPath)
                    graphicList.append(graphic)
                }
            }
        }
    }
    
    func getRandom() -> Graphic? {
        return graphicList.randomElement()
    }
    
    // Add a method to get the count of graphics
    func count() -> Int {
        return graphicList.count
    }
    
    // Add a method to get a specific graphic by index
    func graphic(at index: Int) -> Graphic? {
        guard index >= 0 && index < graphicList.count else { return nil }
        return graphicList[index]
    }
}


// MARK: - ImageGallery View Controller
class ImageGalleryViewController: NSViewController {
    private var library: ImageLibrary
    private var scrollView: NSScrollView!
    private let itemSize = NSSize(width: 150, height: 150)
    private let spacing: CGFloat = 20
    
    init(library: ImageLibrary) {
        self.library = library
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func loadView() {
        view = NSView(frame: NSRect(x: 0, y: 0, width: 800, height: 600))
        setupScrollView()
        loadImages()
    }
    
    private func setupScrollView() {
        scrollView = NSScrollView(frame: view.bounds)
        scrollView.hasVerticalScroller = true
        scrollView.hasHorizontalScroller = false
        scrollView.autoresizingMask = [.width, .height]
        
        let contentView = NSView(frame: scrollView.bounds)
        contentView.wantsLayer = true
        contentView.layer?.backgroundColor = NSColor.windowBackgroundColor.cgColor
        
        scrollView.documentView = contentView
        
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scrollView)
        
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }
    
    private func loadImages() {
        guard let contentView = scrollView.documentView else { return }
        
        let itemsPerRow = Int(view.bounds.width / (itemSize.width + spacing))
        var currentX: CGFloat = spacing
        var currentY: CGFloat = spacing
        var maxY: CGFloat = 0
        
        for index in 0..<library.count() {
            guard let graphic = library.graphic(at: index) else { continue }
            
            // Create image view
            let imageView = NSImageView(frame: NSRect(x: currentX, 
                                                    y: currentY, 
                                                    width: itemSize.width, 
                                                    height: itemSize.height))
            imageView.image = graphic.getImage(size: itemSize)
            imageView.imageScaling = .scaleProportionallyUpOrDown
            
            contentView.addSubview(imageView)
            
            // Update positions
            currentX += itemSize.width + spacing
            maxY = max(maxY, currentY + itemSize.height + spacing)
            
            // Move to next row if needed
            if (index + 1) % itemsPerRow == 0 {
                currentX = spacing
                currentY = maxY
            }
        }
        
        // Update content view size
        contentView.frame.size = NSSize(width: view.bounds.width, height: maxY)
    }
}



let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)  // Add this line to make app visible
app.activate(ignoringOtherApps: true)  // Add this line to bring app to front
app.run()  // Replace NSApplicationMain with this
