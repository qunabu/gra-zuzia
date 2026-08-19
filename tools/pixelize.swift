import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

// pixelize <we> <wy> <cropX> <cropY> <cropW> <cropH> <outW> <outH> [nes|surowe]
let a = CommandLine.arguments
guard a.count >= 9 else { fatalError("za mało argumentów") }
let tryb = a.count > 9 ? a[9] : "nes"
let gamma = a.count > 10 ? Double(a[10])! : 1.0      // <1 rozjaśnia
let nasyc = a.count > 11 ? Double(a[11])! : 1.35
let poziomy = a.count > 12 ? Double(a[12])! : 0     // 0 = bez posteryzacji
let kontur  = a.count > 13 ? (a[13] == "kontur") : false

guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: a[1]) as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { fatalError("wczytanie") }
guard let wyc = img.cropping(to: CGRect(x: Int(a[3])!, y: Int(a[4])!,
                                        width: Int(a[5])!, height: Int(a[6])!))
else { fatalError("kadr") }

let ow = Int(a[7])!, oh = Int(a[8])!
let cs = CGColorSpace(name: CGColorSpace.sRGB)!
guard let ctx = CGContext(data: nil, width: ow, height: oh, bitsPerComponent: 8,
                          bytesPerRow: ow*4, space: cs,
                          bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)
else { fatalError("kontekst") }
ctx.interpolationQuality = .high
ctx.draw(wyc, in: CGRect(x: 0, y: 0, width: ow, height: oh))

guard let dane = ctx.data?.assumingMemoryBound(to: UInt8.self) else { fatalError("dane") }

// paleta NES (bez powtórzonych czerni)
let NES: [(Double, Double, Double)] = [
 (0,0,0),(0,42,136),(20,18,167),(59,0,164),(92,0,126),(110,0,64),(108,6,0),(86,29,0),
 (51,53,0),(11,72,0),(0,82,0),(0,79,8),(0,64,77),
 (173,173,173),(21,95,217),(66,64,255),(117,39,254),(160,26,204),(183,30,123),(181,49,32),(153,78,0),
 (107,109,0),(56,135,0),(12,147,0),(0,143,50),(0,124,141),
 (255,254,255),(100,176,255),(146,144,255),(198,118,255),(243,106,255),(254,110,204),(254,129,112),(234,158,34),
 (188,190,0),(136,216,0),(92,228,48),(69,224,130),(72,205,222),(79,79,79),
 (255,254,255),(192,223,255),(211,210,255),(232,200,255),(251,194,255),(254,196,234),(254,204,197),(247,216,165),
 (228,229,148),(207,239,150),(189,244,171),(179,243,204),(181,235,242),(184,184,184)
]

func najblizszy(_ r: Double, _ g: Double, _ b: Double) -> (UInt8, UInt8, UInt8) {
    var naj = 0, najD = Double.infinity
    for (i, k) in NES.enumerated() {
        // ważona odległość – oko jest czulsze na zieleń
        let d = 2.0*(r-k.0)*(r-k.0) + 4.0*(g-k.1)*(g-k.1) + 3.0*(b-k.2)*(b-k.2)
        if d < najD { najD = d; naj = i }
    }
    let k = NES[naj]
    return (UInt8(k.0), UInt8(k.1), UInt8(k.2))
}

var uzyte = Set<String>()
for y in 0..<oh {
    for x in 0..<ow {
        let i = (y*ow + x)*4
        // alfa binarna – pixel art nie ma półprzezroczystości
        if dane[i+3] < 128 {
            dane[i]=0; dane[i+1]=0; dane[i+2]=0; dane[i+3]=0
            continue
        }
        var r = Double(dane[i]), g = Double(dane[i+1]), b = Double(dane[i+2])
        if dane[i+3] < 255 {           // odpremnożenie
            let f = 255.0/Double(dane[i+3])
            r = min(255, r*f); g = min(255, g*f); b = min(255, b*f)
        }
        // gamma (rozjaśnienie cieni) + kontrast + nasycenie
        let gr = 255*pow(r/255, gamma), gg = 255*pow(g/255, gamma), gb = 255*pow(b/255, gamma)
        let sr = 128 + (gr-128)*1.12, sg = 128 + (gg-128)*1.12, sb = 128 + (gb-128)*1.12
        let l = 0.299*sr + 0.587*sg + 0.114*sb
        let nr = min(255, max(0, l + (sr-l)*nasyc))
        let ng = min(255, max(0, l + (sg-l)*nasyc))
        let nb = min(255, max(0, l + (sb-l)*nasyc))
        if tryb == "nes" {
            let (kr, kg, kb) = najblizszy(nr, ng, nb)
            dane[i]=kr; dane[i+1]=kg; dane[i+2]=kb
        } else if poziomy >= 2 {
            func kwant(_ v: Double) -> UInt8 {
                let k = (poziomy - 1)
                return UInt8(max(0, min(255, (v/255*k).rounded() / k * 255)))
            }
            dane[i]=kwant(nr); dane[i+1]=kwant(ng); dane[i+2]=kwant(nb)
        } else {
            dane[i]=UInt8(nr); dane[i+1]=UInt8(ng); dane[i+2]=UInt8(nb)
        }
        dane[i+3]=255
        uzyte.insert("\(dane[i]),\(dane[i+1]),\(dane[i+2])")
    }
}

if kontur {                            // 1-pikselowy czarny kontur wokół sylwetki
    let kopia = UnsafeMutablePointer<UInt8>.allocate(capacity: ow*oh*4)
    kopia.update(from: dane, count: ow*oh*4)
    for y in 0..<oh { for x in 0..<ow {
        let i = (y*ow+x)*4
        if kopia[i+3] != 0 { continue }
        var sasiad = false
        for (dx,dy) in [(-1,0),(1,0),(0,-1),(0,1)] {
            let nx = x+dx, ny = y+dy
            if nx<0 || ny<0 || nx>=ow || ny>=oh { continue }
            if kopia[(ny*ow+nx)*4+3] > 0 { sasiad = true }
        }
        if sasiad { dane[i]=0; dane[i+1]=0; dane[i+2]=0; dane[i+3]=255 }
    }}
}

guard let out = ctx.makeImage(),
      let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[2]) as CFURL,
                                                 UTType.png.identifier as CFString, 1, nil)
else { fatalError("zapis") }
CGImageDestinationAddImage(dest, out, nil)
CGImageDestinationFinalize(dest)
print("zapisano \(a[2]) \(ow)x\(oh), kolorów: \(uzyte.count)")
