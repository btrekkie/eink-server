#ifndef __GENERATED_CONSTANTS_H__
#define __GENERATED_CONSTANTS_H__

// The rotation to use when drawing to the Inkplate device, as in
// Inkplate.setRotation. This is one of the following values:
//
// 1. Portrait right (bottom of device on right)
// 2. Landscape upside down
// 3. Portrait left (bottom of device on left)
// 4. Landscape
extern const int ROTATION;

// The bytes at the beginning of every payload sent to or from the server. We
// use this as a crude way of checking whether we are dealing with a correctly
// formatted payload.
extern const char HEADER[];

// The number of bytes in HEADER
extern const int HEADER_LENGTH;

// Bytes identifying the version of the protocol that this program uses to
// communicate with the server
extern const char PROTOCOL_VERSION[];

// The number of bytes in PROTOCOL_VERSION
extern const int PROTOCOL_VERSION_LENGTH;

// The number of status images, as in the Python class StatusImages
extern const int STATUS_IMAGE_COUNT;

// The number of bytes in each of the status image files, as in the Python class
// StatusImages. This is parallel to STATUS_IMAGE_IDS.
extern const int STATUS_IMAGE_DATA_LENGTHS[];

// The contents of each of the status image files, as in the Python class
// StatusImages. These are files suitable for calls to drawImage. This is
// parallel to STATUS_IMAGE_IDS.
extern const char* STATUS_IMAGE_DATA[];

// The IDs of the status images, in lexicographic (or memcmp) order, as in the
// Python method ServerIO.image_id and the Python class StatusImages.
extern const char* STATUS_IMAGE_IDS[];

// The indices in STATUS_IMAGE_IDS of the typed status images, as in the Python
// class StatusImages. Given a StatusImageType T,
// STATUS_IMAGE_IDS[STATUS_IMAGES_BY_TYPE[(int)T]] is for the status image of
// that type.
extern const int STATUS_IMAGES_BY_TYPE[];

// The URLs of the servers, in the order we should attempt to reach them
extern const char* TRANSPORT_URLS[];

// The number of elements in WI_FI_SSIDS
extern const int WI_FI_NETWORK_COUNT;

// The SSIDs of the Wi-Fi networks we may connect to, in the order we should try
// to connect to them. Note that this may contain duplicates. In theory, the
// user may want to try multiple different passwords for a given SSID.
extern const char* WI_FI_SSIDS[];

// The indices in WI_FI_SSIDS of the SSIDs in strcmp order.
// WI_FI_SSIDS[WI_FI_NETWORK_INDICES[i]] is the (i + 1)th SSID "alphabetically."
// Ties are broken arbitrarily.
extern const int WI_FI_NETWORK_INDICES[];

#endif
