//! Installed-product identity shared by the Driver binary and embedded SDK
//! hosts. Release and source builds keep separate per-user homes, so both
//! resolve the extension store from the same canonical executable test.

use std::path::Path;

pub const LOCAL_CLI_NAME: &str = "cua-driver-local";

pub fn path_is_local(path: &Path) -> bool {
    let file_name = path
        .file_name()
        .and_then(|name| name.to_str())
        .unwrap_or_default();
    file_name == LOCAL_CLI_NAME
        || file_name == format!("{LOCAL_CLI_NAME}.exe")
        || path
            .components()
            .any(|component| component.as_os_str().to_str() == Some("CuaDriverLocal.app"))
}

/// Whether this process is the explicitly-installed source-build product.
pub fn is_local_installation() -> bool {
    std::env::current_exe()
        .ok()
        .and_then(|path| std::fs::canonicalize(path).ok())
        .is_some_and(|path| path_is_local(&path))
}

pub fn user_home_subdirectory() -> &'static str {
    if is_local_installation() {
        ".cua-driver-local"
    } else {
        ".cua-driver"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn local_identity_requires_the_explicit_local_product_name() {
        assert!(path_is_local(Path::new(
            "/Applications/CuaDriverLocal.app/Contents/MacOS/cua-driver-local"
        )));
        assert!(path_is_local(Path::new(
            "/dev/.cua-driver-local/cua-driver-local.exe"
        )));
        assert!(!path_is_local(Path::new(
            "/Applications/CuaDriver.app/Contents/MacOS/cua-driver"
        )));
        assert!(!path_is_local(Path::new("/tmp/cua-driver-local-test")));
    }
}
