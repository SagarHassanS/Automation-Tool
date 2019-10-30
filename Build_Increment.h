#ifndef _SVN_VERSION_H_
#define _SVN_VERSION_H_

#define SVN_LOCAL_MODIFICATIONS $WCMODS?1:0$  // 1 if there are modifications to the local working copy, 0 otherwise
#define SVN_REVISION            $WCREV$       // Highest committed revision number in the working copy
#define SVN_TIME_NOW            $WCNOW$       // Current system date &amp; time
#define BUILD_VERSION_MAJOR     13
#define BUILD_VERSION_MINOR     0
#define BUILD_VERSION_REVISION  1
#define BUILD_INCREMENT 210
#endif
