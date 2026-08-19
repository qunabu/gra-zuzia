import Foundation
import CoreGraphics
import ImageIO
import Vision
import UniformTypeIdentifiers
import CoreImage

// usage: cutout <input> <output> <x> <y> <w> <h>
let args = CommandLine.arguments
let inPath = args[1]
let outPath = args[2]
let cx = Int(args[3])!, cy = Int(args[4])!, cw = Int(args[5])!, ch = Int(args[6])!

guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: inPath) as CFURL, nil),
      let full = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    fatalError("cannot load")
}
print("full size: \(full.width)x\(full.height)")
guard let crop = full.cropping(to: CGRect(x: cx, y: cy, width: cw, height: ch)) else {
    fatalError("crop failed")
}
print("crop size: \(crop.width)x\(crop.height)")

let request = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(cgImage: crop, options: [:])
try handler.perform([request])

guard let obs = request.results?.first else { fatalError("no subject found") }
print("instances: \(obs.allInstances.count)")

let maskBuf = try obs.generateScaledMaskForImage(forInstances: obs.allInstances, from: handler)

let ciMask = CIImage(cvPixelBuffer: maskBuf)
let ciImg = CIImage(cgImage: crop)
let scaleX = ciImg.extent.width / ciMask.extent.width
let scaleY = ciImg.extent.height / ciMask.extent.height
let scaledMask = ciMask.transformed(by: CGAffineTransform(scaleX: scaleX, y: scaleY))

let filter = CIFilter(name: "CIBlendWithMask")!
filter.setValue(ciImg, forKey: kCIInputImageKey)
filter.setValue(CIImage.empty(), forKey: kCIInputBackgroundImageKey)
filter.setValue(scaledMask, forKey: kCIInputMaskImageKey)
let output = filter.outputImage!.cropped(to: ciImg.extent)

let ctx = CIContext()
let cs = CGColorSpace(name: CGColorSpace.sRGB)!
try ctx.writePNGRepresentation(of: output, to: URL(fileURLWithPath: outPath), format: .RGBA8, colorSpace: cs)
print("wrote \(outPath)")
