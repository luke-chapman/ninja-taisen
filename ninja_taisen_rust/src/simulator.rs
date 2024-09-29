// We represent each card as a byte, i.e. in the range 0-255
// The encoding for each of the bits is as follows:
// 0:        0=null, 1=non-null
// 1:        0=monkey, 1=wolf
// 2,3:      [0,0]=rock, [0,1]=paper, [1,0]=scissors, [1,1]=joker
// 4,5,6,7:  encodes strength i.e. 1, 2, 3 or 4
//
// Of the 255 available values, the 29 we expect to use are detailed in the below enum
#[repr(u8)]
enum Card {
    NULL = 0,

    MR1 = 129,
    MR2 = 130,
    MR3 = 131,

    MP1 = 145,
    MP2 = 146,
    MP3 = 147,

    MS1 = 161,
    MS2 = 162,
    MS3 = 163,

    MJ0 = 176,
    MJ1 = 177,
    MJ2 = 178,
    MJ3 = 179,
    MJ4 = 180,

    WR1 = 193,
    WR2 = 194,
    WR3 = 195,

    WP1 = 209,
    WP2 = 210,
    WP3 = 211,

    WS1 = 225,
    WS2 = 226,
    WS3 = 227,

    WJ0 = 240,
    WJ1 = 241,
    WJ2 = 242,
    WJ3 = 243,
    WJ4 = 244,
}

struct Board {
    cards: [Card; 220]
}
